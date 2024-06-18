# -*- coding: utf-8 -*-
"""Pipeline tools for AYON motionbuilder integration."""
import os
from operator import attrgetter
import logging
import json

from ayon_core.host import HostBase, IWorkfileHost, ILoadHost, IPublishHost
import pyblish.api
from ayon_core.pipeline import (
    register_creator_plugin_path,
    register_loader_plugin_path,
    AVALON_CONTAINER_ID,
    AYON_CONTAINER_ID,
)
from ayon_motionbuilder import MOTION_BUILDER_ADDON_ROOT
from ayon_motionbuilder.api.menu import AYONMenu
from ayon_motionbuilder.api import lib

from pyfbsdk import (
    FBApplication,
    FBSystem,
    FBFbxOptions,
    FBSet,
    FBNamespaceAction,
    FBPropertyType
)

log = logging.getLogger("ayon_motionbuilder")

PLUGINS_DIR = os.path.join(MOTION_BUILDER_ADDON_ROOT, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")
INVENTORY_PATH = os.path.join(PLUGINS_DIR, "inventory")


class MotionBuilderHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):

    name = "motionbuilder"

    def __init__(self):
        super(MotionBuilderHost, self).__init__()
        self._op_events = {}
        self._has_been_setup = False

    def install(self):
        pyblish.api.register_host("motionbuilder")

        pyblish.api.register_plugin_path(PUBLISH_PATH)
        register_loader_plugin_path(LOAD_PATH)
        register_creator_plugin_path(CREATE_PATH)

        # self._register_callbacks()
        self.menu = AYONMenu()

        self._has_been_setup = True

    def workfile_has_unsaved_changes(self):
        return FBApplication().IsSceneModified()

    def get_workfile_extensions(self):
        return [".fbx"]

    def save_workfile(self, dst_path=None):
        FBApplication().FileSave(dst_path)
        return dst_path

    def open_workfile(self, filepath):
        loadOptions = FBFbxOptions(True)
        FBApplication().FileOpen(filepath, True, loadOptions)
        return filepath

    def get_current_workfile(self):
        return FBApplication().FBXFileName

    def get_containers(self):
        return ls()

    @staticmethod
    def create_context_node():
        FBSystem().Scene.PropertyCreate(
            "AyonContext", FBPropertyType.kFBPT_charptr,
            "{}", False, True, None)


    def update_context_data(self, data, changes):
        for context in FBSystem().Scene.PropertyList:
            if context.GetName() in {"AyonContext"}:
                context.Data = json.dumps(data)
            else:
                self.create_context_node()

    def get_context_data(self):
        ayon_context = "{}"
        for context in FBSystem().Scene.PropertyList:
            if context.GetName() == "AyonContext":
                ayon_context = context.AsString()

        return json.loads(ayon_context)


def parse_container(container):
    """Return the container node's full container data.

    Args:
        container (str): A container node name.

    Returns:
        dict: The container schema data for this container node.

    """
    data = lib.read(container)

    # Backwards compatibility pre-schemas for containers
    data["schema"] = data.get("schema", "openpype:container-3.0")

    # Append transient data
    data["objectName"] = container.Name
    return data


def ls():
    """Get all AYON containers."""
    containers = []
    for obj_sets in FBSystem().Scene.Sets:
        for prop in obj_sets.PropertyList:
            if prop.AsString() in {
                AYON_CONTAINER_ID, AVALON_CONTAINER_ID
                }:
                    containers.append(obj_sets)

    for container in sorted(containers, key=attrgetter("Name")):
        yield parse_container(container)


def containerise(name: str, context, objects, namespace=None, loader=None,
                 suffix="_CON"):
    data = {
        "schema": "openpype:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace or "",
        "loader": loader,
        "representation": context["representation"]["id"],
    }
    container_name = f"{name}{suffix}"
    container_group = FBSet(container_name)
    for obj in objects:
        container_group.ConnectSrc(obj)
        container_group.PickUp = True
    container_group.ProcessObjectNamespace(
        FBNamespaceAction.kFBConcatNamespace, namespace)
    for key, value in data.items():
        container_group.PropertyCreate(
            key, FBPropertyType.kFBPT_charptr, value, False, True, None)
        target_param = container_group.PropertyList.Find(key)
        target_param.Data = value
    if not lib.imprint(container_name, data):
        print(f"imprinting of {container_name} failed.")
    return container_group
