import os
import pyblish.api
from ayon_core.pipeline import publish
from ayon_motionbuilder.api.lib import maintain_selection
from pyfbsdk import FBApplication, FBFbxOptions, FBSystem


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
        saveOptions = FBFbxOptions(False)
        creator_attributes = instance.data["creator_attributes"]
        saveOptions.EmbedMedia = (
            True if creator_attributes.get("EmbedMedia")
            else False)
        saveOptions.KeepTransformHierarchy = (
            True if creator_attributes.get("KeepTransformHierarchy")
            else False)
        # TODO: Select the model which needs to export
        saveOptions.SaveSelectedModelsOnly = (
            True if creator_attributes.get("SaveSelectedModelsOnly")
            else False)
        selected_nodes = [node for node in
                          FBSystem().Scene.RootModel.Children
                          if node.Name in instance.data.get(
                              "selected_nodes", [])]
        with maintain_selection(selected_nodes):
            app.FileSave(filepath, saveOptions)

        representation = {
            'name': 'fbx',
            'ext': 'fbx',
            'files': asset_filename,
            "stagingDir": staging_dir,
        }
        instance.data["representations"].append(representation)
