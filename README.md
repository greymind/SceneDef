# Greymind SceneDef
Scene file format with Maya Exporter and C# Importer.
> Depends on [ModelDef](https://github.com/greymind/ModelDef)

# Features
* Scene graph - position, rotation, scale
* Custom physics shape
* Lights - point, directional, spot
* Cameras
* Exports each scene fixture as [ModelDef](https://github.com/greymind/ModelDef)
* Create lightmap UV sets
* Combine and reparent scene objects

# Installation
Place the `SceneExporter.py` and `Common.py` files in `Documents\maya\<maya version>\scripts` folder.

# Usage

## Export
To invoke this script, use the following commands in the python mode of the script editor:
```
import SceneExporter as Se
reload(Se)
Se.Run()
```
You may middle-mouse drag these lines to the shelf to create a shortcut toolbar button.

## Import
Copy all the files to your project and use the `Load` and `Save` methods of `FixtureXml`.

# Team
* [Balakrishnan (Balki) Ranganathan](http://greymind.com)

# License
* MIT

