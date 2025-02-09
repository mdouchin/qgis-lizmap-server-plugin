__copyright__ = 'Copyright 2022, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import logging
import sys
import warnings

from typing import NamedTuple, Union

from qgis.core import Qgis
from qgis.PyQt import Qt
from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QFontDatabase
from qgis.server import QgsServerOgcApi, QgsServerOgcApiHandler

from lizmap_server.exception import ServiceError
from lizmap_server.tools import check_environment_variable, to_bool

LOGGER = logging.getLogger('Lizmap')

try:
    # Py-QGIS-Server
    # noinspection PyUnresolvedReferences
    from pyqgisserver.plugins import plugin_list, plugin_metadata
    IS_PY_QGIS_SERVER = True
except ImportError:
    # FCGI and others
    from qgis.utils import pluginMetadata, server_active_plugins
    IS_PY_QGIS_SERVER = False

    def plugin_list() -> list:
        """ To match Py-QGIS-Server API."""
        return server_active_plugins

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from osgeo import gdal


def plugin_metadata_key(name: str, key: str, ) -> str:
    """ Return the version for a given plugin. """
    unknown = 'unknown'
    # it seems configparser is transforming all keys as lowercase...
    if IS_PY_QGIS_SERVER:
        metadata = plugin_metadata(name)
        value = metadata['general'].get(key, None)
        if value:
            return value
        return metadata['general'].get(key.lower(), unknown)
    else:
        value = pluginMetadata(name, key)
        if value not in ("__error__", ""):
            return value
        value = pluginMetadata(name.lower(), key)
        if value not in ("__error__", ""):
            return value
        return unknown


PyQgisServer = NamedTuple(
    "PyQgisServer", [
        ('version', str),
        ('build_id', Union[int, None]),
        ('commit_id', Union[int, None]),
        ('is_stable', bool)
    ]
)


def py_qgis_server_info() -> PyQgisServer:
    """ Return the Py-QGIS-Server version or an empty string. """
    version = 'not used'
    build_id = None
    commit_id = None
    is_stable = False
    if not IS_PY_QGIS_SERVER:
        return PyQgisServer(version, build_id, commit_id, is_stable)

    # noinspection PyBroadException
    try:
        from pyqgisserver.version import __manifest__, __version__
        version = __version__
        build_id = __manifest__.get('buildid')
        commit_id = __manifest__.get('commitid')
        is_stable = not any(x in version for x in ("pre", "alpha", "beta", "rc"))
        return PyQgisServer(version, build_id, commit_id, is_stable)
    except Exception:
        msg = 'error while fetching py-qgis-server version'
        LOGGER.error(msg)
        return PyQgisServer(msg, build_id, commit_id, is_stable)


class ServerInfoHandler(QgsServerOgcApiHandler):

    def path(self):
        return QRegularExpression("server.json")

    def summary(self):
        return "Server information"

    def description(self):
        return "Get info about the current QGIS server"

    def operationId(self):
        return "server"

    def linkTitle(self):
        return "Handler Lizmap API server info"

    def linkType(self):
        return QgsServerOgcApi.data

    def handleRequest(self, context):
        if not check_environment_variable():
            raise ServiceError("Bad request error", "Invalid request", 404)

        # 'name' is not the folder name in the 'expected_list' variable, it can be different
        keys = ('name', 'version', 'commitNumber', 'commitSha1', 'dateTime', 'repository')
        plugins = dict()
        for plugin in plugin_list():
            plugins[plugin] = dict()
            for key in keys:
                plugins[plugin][key] = plugin_metadata_key(plugin, key)

        expected_list = (
            'wfsOutputExtension',
            # 'cadastre', very specific for the French use-case
            'lizmap_server',
            'atlasprint',
            # waiting a little for these one
            # 'tilesForServer',
            # 'DataPlotly',
        )

        for expected in expected_list:
            if expected not in plugins.keys():
                plugins[expected] = {'version': 'not found'}

        qgis_version_split = Qgis.QGIS_VERSION.split('-')

        services_available = []
        expected_services = ('WMS', 'WFS', 'WCS', 'WMTS', 'ATLAS', 'CADASTRE', 'EXPRESSION', 'LIZMAP')
        for service in expected_services:
            if context.serverInterface().serviceRegistry().getService(service):
                services_available.append(service)

        if Qgis.QGIS_VERSION_INT >= 31200 and Qgis.devVersion() != 'exported':
            commit_id = Qgis.devVersion()
        else:
            commit_id = ''

        # noinspection PyBroadException
        try:
            # Format the tag according to QGIS git repository
            tag = 'final-{}'.format(qgis_version_split[0].replace('.', '_'))
        except Exception:
            tag = ""

        py_qgis_server_metadata = py_qgis_server_info()
        data = {
            'qgis_server': {
                'metadata': {
                    'version': qgis_version_split[0],  # 3.16.0
                    'tag': tag,  # final-3_16_0
                    'name': qgis_version_split[1],  # Hannover
                    'commit_id': commit_id,  # 288d2cacb5 if it's a dev version
                    'version_int': Qgis.QGIS_VERSION_INT,  # 31600
                    'py_qgis_server': IS_PY_QGIS_SERVER,  # bool, # deprecated since 28/10/2022
                    'py_qgis_server_version': py_qgis_server_metadata.version,  # str, deprecated since 28/10/2022
                },
                'py_qgis_server': {
                    'found': IS_PY_QGIS_SERVER,
                    'version': py_qgis_server_metadata.version,
                    'build_id': py_qgis_server_metadata.build_id,
                    'commit_id': py_qgis_server_metadata.commit_id,
                    'stable_release': py_qgis_server_metadata.is_stable,  # bool, deprecated since 16/12/2022
                    'stable': py_qgis_server_metadata.is_stable,
                },
                # 'support_custom_headers': self.support_custom_headers(),
                'services': services_available,
                'plugins': plugins,
            },
            'fonts': QFontDatabase().families(),
            'environment': {
                'gdal': gdal.VersionInfo('VERSION_NUM'),
                'python': sys.version,
                'qt': Qt.QT_VERSION_STR,
            }
        }
        self.write(data, context)

    def support_custom_headers(self) -> Union[None, bool]:
        """ Check if this QGIS Server supports custom headers.

         Returns None if the check is not requested with the GET parameter CHECK_CUSTOM_HEADERS

         If requested, returns boolean if X-Check-Custom-Headers is found in headers.
         """
        handler = self.serverIface().requestHandler()

        params = handler.parameterMap()
        if not to_bool(params.get('CHECK_CUSTOM_HEADERS')):
            return None

        headers = handler.requestHeaders()
        return headers.get('X-Check-Custom-Headers') is not None

    def parameters(self, context):
        from qgis.server import QgsServerQueryStringParameter
        return [
            QgsServerQueryStringParameter(
                "CHECK_CUSTOM_HEADERS",
                False,
                QgsServerQueryStringParameter.Type.String,
                "If we check custom headers"
            ),
        ]
