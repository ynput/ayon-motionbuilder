"""Motion Builder specific AYON/Pyblish plugin definitions."""
from ayon_core.lib import BoolDef
from ayon_core.pipeline import (
    CreatedInstance,
    Creator,
    AYON_INSTANCE_ID,
    AVALON_INSTANCE_ID,
)

from pyfbsdk import FBSet, FBSystem
from .lib import (
    lsattr,
    instances_imprint,
    read,
    get_node_by_name,
    load_data_from_parameter,
)


class MotionBuilderCreatorBase(object):

    @staticmethod
    def cache_instance_data(shared_data):
        if shared_data.get("mbuilder_cached_instances") is not None:
            return shared_data

        shared_data["mbuilder_cached_instances"] = {}

        cached_instances = []
        for id_type in [AYON_INSTANCE_ID, AVALON_INSTANCE_ID]:
            cached_instances.extend(lsattr("id", id_type))

        for i in cached_instances:
            instances_param = i.PropertyList.Find("instances")
            data = load_data_from_parameter(instances_param)
            creator_id = data.get("creator_identifier")
            if creator_id not in shared_data["mbuilder_cached_instances"]:
                shared_data["mbuilder_cached_instances"][creator_id] = [i.Name]
            else:
                shared_data[
                    "mbuilder_cached_instances"][creator_id].append(i.Name)

    def create_node(self, product_name):
        container_node = get_node_by_name(product_name)
        if not container_node:
            container_node = FBSet(product_name)
            return container_node.Name

class MotionBuilderCreator(Creator, MotionBuilderCreatorBase):

    def create(self, product_name, instance_data, pre_create_data):
        creator_attributes = instance_data.setdefault(
            "creator_attributes", {})
        for key in [
            "EmbedMedia",
            "SaveSelectedModelsOnly",
            "KeepTransformHierarchy",
        ]:
            if key in pre_create_data:
                creator_attributes[key] = pre_create_data[key]
        instance_node = self.create_node(product_name)
        instance_data["instance_node"] = instance_node
        # TODO: supports to select models to be published
        if pre_create_data.get("SaveSelectedModelsOnly"):
            instance_data["selected_nodes"] = [
                sel.Name for sel in get_selection()
            ]
            node = get_node_by_name(instance_node)
            if node:
                for sel in get_selection():
                    node.ConnectSrc(sel)

        instance = CreatedInstance(
            self.product_type,
            product_name,
            instance_data,
            self
        )
        self._add_instance_to_context(instance)
        instances_imprint(instance_node, instance.data_to_store())
        return instance

    def collect_instances(self):
        self.cache_instance_data(self.collection_shared_data)
        cached_instances = self.collection_shared_data["mbuilder_cached_instances"]
        for instance in cached_instances.get(self.identifier, []):
            created_instance = CreatedInstance.from_existing(
                read(get_node_by_name(instance)), self
            )
            self._add_instance_to_context(created_instance)

    def update_instances(self, update_list):
        for created_inst, changes in update_list:
            instance_node = created_inst.get("instance_node")
            new_values = {
                key: changes[key].new_value
                for key in changes.changed_keys
            }
            product_name = new_values.get("productName", "")
            if product_name and instance_node != product_name:
                new_product_name = new_values["productName"]
                node = get_node_by_name(instance_node)
                instance_node = new_product_name
                created_inst["instance_node"] = instance_node
                node.Name = instance_node

            instances_imprint(
                instance_node,
                created_inst.data_to_store()
            )

    def remove_instances(self, instances):
        """Remove specified instance from the scene.

        This is only removing `id` parameter so instance is no longer
        instance, because it might contain valuable data for artist.

        """
        for instance in instances:
            instance_node = get_node_by_name(instance.data.get("instance_node"))
            if instance_node:
               instance_node.FBDelete()
            self._remove_instance_from_context(instance)

    def get_instance_attr_defs(self):
        return [
            BoolDef("EmbedMedia",
                    label="Embed Media"),
            BoolDef("SaveSelectedModelsOnly",
                    label="Save Selected Models Only"),
            BoolDef("KeepTransformHierarchy",
                    label="Keep Transform Hierarchy"),
        ]

    def get_pre_create_attr_defs(self):
        return self.get_instance_attr_defs()

def get_selection():
    return [
        component for component in FBSystem().Scene.Components
        if component.Selected == True
    ]
