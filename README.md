## [![logo](lizmap/resources/icons/icon.png "3Liz")][3liz]Lizmap QGIS Plugin

* Latest download link: https://plugins.qgis.org/plugins/lizmap/version/3.2.7/download/
* All versions are available [here](https://plugins.qgis.org/plugins/lizmap/)
* Do not use the link provided by GitHub by default.

Banches :

* The [dev](https://github.com/3liz/lizmap-plugin/tree/dev) branch is for the next release of [LWC](https://github.com/3liz/lizmap-web-client/). 
* The [master](https://github.com/3liz/lizmap-plugin/tree/master) branch is for the actual released version on [qgis.org](https://plugins.qgis.org) and compatible with the current of [LWC](https://github.com/3liz/lizmap-web-client/). 

Publication plugin for Lizmap Web Application, by 3LIZ.

```
begin       : 2011-11-01
copyright   : (C) 2011 by 3liz
authors     : René-Luc D'Hont and Michaël Douchin
email       : info@3liz.com
website     : http://www.3liz.com
```

Lizmap QGIS plugin aims to be used to configure a web application dynamically generated by Lizmap (PHP/JavaScript application) with the help of QGIS Server.
With this plugin, you can configure one web map per QGIS project. The Lizmap web application must be installed on the server.

The original Code is 3liz code.

You can find help and news by subscribing to the mailing list: https://lists.osgeo.org/mailman/listinfo/lizmap.

For more detailed information, check the [Lizmap Web Client](https://github.com/3liz/lizmap-web-client/) GitHub repository.

### Authors

The Initial Developer of the Original Code are René-Luc D'Hont <rldhont@3liz.com> and Michael Douchin <mdouchin@3liz.com>.
Portions created by the Initial Developer are Copyright (C) 2011 the Initial Developer.
All Rights Reserved.

### Installation of the Lizmap plugin

This does not cover the installation of Lizmap Web Client application.

From QGIS application:

1. Plugins menu -> Manage and Install Plugins...
1. Select LizMap plugin from Not installed list
1. Install plugin

or from GitHub repository:

1. Clone the repo: `git clone --recursive git@github.com:3liz/lizmap-plugin.git lizmap`
1. `mv lizmap ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

If it's from a previous GitHub repository:
1. `git submodule update` to update the submodule.

### Documentation

[English doc](https://docs.lizmap.com/current/en/)

[French doc](https://docs.lizmap.com/current/fr)

[GitHub documentation](https://github.com/3liz/lizmap-documentation)

### Contributors

* Salvatore Larosa  @slarosa
* Paolo Cavallini @pcav
* Arnaud Deleurme
* @ewsterrenburg
* Sławomir Bienias @SaekBinko
* Petr Tsymbarovich @mentaljam
* Víctor Herreros @vherreros
* João Gaspar
* Felix Kuehne
* Kari Salovaara
* Xan Vieiro
* Etienne Trimaille @Gustry
* José Macau

*Please propose a PR to add yourself if you are missing*

### License

Version: MPL 2.0/GPL 2.0/LGPL 2.1

The contents of this file are subject to the Mozilla Public License Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.mozilla.org/MPL/

Alternatively, the contents of this file may be used under the terms of either of the GNU General Public License Version 2 or later (the "GPL"), or the GNU Lesser General Public License Version 2.1 or later (the "LGPL"), in which case the provisions of the GPL or the LGPL are applicable instead of those above. If you wish to allow use of your version of this file only under the terms of either the GPL or the LGPL, and not to allow others to use your version of this file under the terms of the MPL, indicate your decision by deleting the provisions above and replace them with the notice and other provisions required by the GPL or the LGPL. If you do not delete the provisions above, a recipient may use your version of this file under the terms of any one of the MPL, the GPL or the LGPL.

Software distributed under the License is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the specific language governing rights and limitations under the License.

[3liz]:http://www.3liz.com

### API

You can use the `lizmap_api` class of `lizmap.py` to get the Lizmap JSON configuration for a specific project.

For example:

```python3
import sys,os
qgisPrefixPath = "/usr/local/"
sys.path.append(os.path.join(qgisPrefixPath, "share/qgis/python/"))
sys.path.append(os.path.join(qgisPrefixPath, "share/qgis/python/plugins/"))
os.environ["QGIS_DEBUG"] = '-1'
os.environ['QGIS_PREFIX_PATH'] = qgisPrefixPath

from qgis.core import QgsApplication
QgsApplication.setPrefixPath(qgisPrefixPath, True)
app = QgsApplication([], False)
app.initQgis()

# Run the lizmap config exporter
from lizmap import lizmap
project_path = '/home/mdouchin/test_a_sup.qgs'
lv = lizmap.LizmapConfig(project_path)
if lv:
    # get the JSON content with default values
    json_content = lv.to_json()

    # OR:

    # get the JSON content with user defined values
    my_global_options = {
        'mapScales': [1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000], # set the map scales
        'osmMapnik': True, # add the OSM mapnik baselayer
        'osmStamenToner': True, # add the OSM Stamen Toner baselayer
        'print': True # activate the print tool
    }
    my_layer_options = {
        'MY LAYER NAME': {
            'title': 'My new title', # change title
            'popup': True, # active popup
            'cached': True, # activate server cache
            'singleTile': False, # set tiled mode on
            'imageFormat': "image/jpeg", # set image format
            'toggled': False # do not display the layer at project startup
        }
    }
    json_content = lv.to_json(
        p_global_options=my_global_options,
        p_layer_options=my_layer_options
    )
    print(json_content)

    # get the configuration as dictionary
    dic_content = lv.lizmap_json_config

# Exit
QgsApplication.exitQgis()
app.exit()
```

# Debug

The `dev` branch is automatically on debug mode. Python exceptions will be re-raised when they occurred. 
On the `master` branch, you can switch to debug mode by adding `-beta` to the version number in the `metadata.txt`.
You can notice if you are on debug mode by checking the Lizmap dialog title (if you can read `DEV Lizmap version number`).

# Attributions

* Some icons come from https://loading.io/ with the Loading.io BY License
