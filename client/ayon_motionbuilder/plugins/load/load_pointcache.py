from ayon_core.pipeline import load, get_representation_path
from ayon_motionbuilder.api.pipeline import containerise
from ayon_motionbuilder.api.lib import (
    unique_namespace, imprint, get_node_by_name
)
from pyfbsdk import (
    FBApplication,
    FBElementAction,
    FBComponentList,
    FBFbxOptions,
    FBFindObjectsByName
)


class PointCacheLoader(load.LoaderPlugin):
    """Motion Builder Point Cache Loader."""

    product_types = {"model", "animation", "rig", "camera"}
    representations = {"fbx"}
    order = -9
    icon = "code-fork"
    color = "white"

    def load(self, context, name=None, namespace=None, data=None):
        app = FBApplication()
        loadOptions = FBFbxOptions(True)
        loadOptions.SetAll(FBElementAction.kFBElementActionAppend, True)
        namespace = unique_namespace(name + "_", suffix="_")
        loadOptions.NamespaceList = namespace
        filename = self.filepath_from_context(context)
        app.FileAppend(filename, True, loadOptions)
        component_List = FBComponentList()
        FBFindObjectsByName(( f"{namespace}:*"), component_List, True, False)
        objects = [obj for obj in component_List]
        return containerise(
            name, context, objects, namespace=namespace,
            loader=self.__class__.__name__
        )

    def update(self, container, context):
        app = FBApplication()
        repre_entity = context["representation"]
        namespace = repre_entity["namespace"]
        path = get_representation_path(repre_entity)
        loadOptions = FBFbxOptions(True)
        loadOptions.NamespaceList = namespace
        loadOptions.SetAll(FBElementAction.kFBElementActionAppend, True)
        app.FileMerge(path, True, loadOptions)
        imprint(container["instance_node"],
                {"representation": repre_entity["id"]})

    def switch(self, container, context):
        self.update(container, context)

    def remove(self, container):
        namespace = container["namespace"]
        component_List = FBComponentList()
        FBFindObjectsByName(( f"{namespace}:*"), component_List, True, False)
        objects = [obj for obj in component_List]
        for obj in objects:
            obj.FBDelete()
