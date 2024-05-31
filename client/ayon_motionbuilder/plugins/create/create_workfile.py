# -*- coding: utf-8 -*-
"""Creator plugin for creating workfiles."""
import ayon_api

from ayon_core.pipeline import CreatedInstance, AutoCreator
from ayon_motionbuilder.api import plugin
from ayon_motionbuilder.api.lib import read, imprint
from pyfbsdk import (
    FBSet,
    FBComponentList,
    FBFindObjectsByName
)


class CreateWorkfile(plugin.MotionBuilderCreatorBase, AutoCreator):
    """Workfile auto-creator."""
    identifier = "io.ayon.creators.motionbuilder.workfile"
    label = "Workfile"
    product_type = "workfile"
    icon = "fa5.file"

    default_variant = "Main"

    settings_category = "motionbuilder"

    def create(self):
        variant = self.default_variant
        current_instance = next(
            (
                instance for instance in self.create_context.instances
                if instance.creator_identifier == self.identifier
            ), None)
        project_name = self.project_name
        folder_path = self.create_context.get_current_folder_path()
        task_name = self.create_context.get_current_task_name()
        host_name = self.create_context.host_name

        if current_instance is None:
            folder_entity = ayon_api.get_folder_by_path(
                project_name, folder_path
            )
            task_entity = ayon_api.get_task_by_name(
                project_name, folder_entity["id"], task_name
            )
            product_name = self.get_product_name(
                project_name,
                folder_entity,
                task_entity,
                variant,
                host_name,
            )
            data = {
                "folderPath": folder_path,
                "task": task_name,
                "variant": variant
            }

            data.update(
                self.get_dynamic_data(
                    project_name,
                    folder_entity,
                    task_entity,
                    variant,
                    host_name,
                    current_instance)
            )
            self.log.info("Auto-creating workfile instance...")
            instance_node = self.create_node(product_name)
            data["instance_node"] = instance_node.Name
            current_instance = CreatedInstance(
                self.product_type, product_name, data, self
            )
            self._add_instance_to_context(current_instance)
            imprint(instance_node, current_instance.data)
        elif (
            current_instance["folderPath"] != folder_path
            or current_instance["task"] != task_name
        ):
            # Update instance context if is not the same
            folder_entity = ayon_api.get_folder_by_path(
                project_name, folder_path
            )
            task_entity = ayon_api.get_task_by_name(
                project_name, folder_entity["id"], task_name
            )
            product_name = self.get_product_name(
                project_name,
                folder_entity,
                task_entity,
                variant,
                host_name,
            )

            current_instance["folderPath"] = folder_entity["path"]
            current_instance["task"] = task_name
            current_instance["productName"] = product_name

    def collect_instances(self):
        self.cache_instance_data(self.collection_shared_data)
        cached_instances = self.collection_shared_data["mbuilder_cached_instances"]
        for instance in cached_instances.get(self.identifier, []):
            cl = FBComponentList()
            FBFindObjectsByName((f"{instance}"), cl, True, True)
            node = next((c for c in cl), None)
            created_instance = CreatedInstance.from_existing(
                read(node), self
            )
            self._add_instance_to_context(created_instance)

    def update_instances(self, update_list):
        for created_inst, _ in update_list:
            instance_node = created_inst.get("instance_node")
            imprint(
                instance_node.Name,
                created_inst.data_to_store()
            )

    def create_node(self, product_name):
        cl = FBComponentList()
        FBFindObjectsByName((f"{product_name}"), cl, True, True)
        node = next((c for c in cl), None)
        if not node:
            node = FBSet(product_name)
            return node
