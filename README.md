# MotionBuilder Addon

This adds integration to Autodesk MotionBuilder. MotionBuilder is a 3D character animation software which users can do virtual cinematography, motion capture and
traditional keyframe animation.

## Settings
Path to Motion Builder executable must be set in the Ayon Setting in `Applications` addon (`ayon+settings://applications/applications/motionbuilder`) and added in `Anatomy`.`Attributes` for particular project to be visible in the Launcher.

### Implemented workflows
Currently supports importing model/rig/animation/camera, exporting animation and saving/opening/publishing workfiles in MotionBuilder integration. All the associated data would be stored in `.zbrushmetadata` folder

## How to start
There is a `create_package.py` python file which contains logic how to create the addon from AYON codebase. Just run the code.
```shell
python ./create_package.py


