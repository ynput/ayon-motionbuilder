import os
import pyblish.api
from ayon_core.pipeline import publish
from pyfbsdk import FBApplication, FBFbxOptions


class ExtractAnimation(publish.Extractor):
    """
    Extract FBX Animation
    """

    order = pyblish.api.ExtractorOrder + 0.001
    label = "Extract Animation"
    hosts = ["motionbuilder"]
    families = ["animation"]

    def process(self, instance):
        staging_dir = self.staging_dir(instance)
        asset_filename = "{name}.fbx".format(**instance.data)

        filepath = os.path.join(
            staging_dir, asset_filename).replace("\\", "/")

        app = FBApplication()
        saveOptions = FBFbxOptions(True)
        app.FileSave(filepath, False, saveOptions)

        representation = {
            'name': 'fbx',
            'ext': 'fbx',
            'files': asset_filename,
            "stagingDir": staging_dir,
        }
        instance.data["representations"].append(representation)
