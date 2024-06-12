import contextlib
import logging
import json
from typing import Union

import six

from pyfbsdk import (
    FBFindObjectsByName,
    FBComponentList,
    FBPropertyType,
    FBSystem
)

JSON_PREFIX = "JSON::"
log = logging.getLogger("ayon_motionbuilder")


def read(container) -> dict:
    data = {}
    props = {
        prop.GetName(): prop.AsString()
        for prop in container.PropertyList if
            prop.GetName() in {
                "schema", "id", "name",
                "namespace", "loader", "representation"
                }
    }
    # this shouldn't happen but let's guard against it anyway
    if not props:
        return data

    for key, value in props.items():
        value = value.strip()
        if isinstance(value.strip(), six.string_types) and \
                value.startswith(JSON_PREFIX):
            with contextlib.suppress(json.JSONDecodeError):
                value = json.loads(value[len(JSON_PREFIX):])

        data[key.strip()] = value

    data["instance_node"] = container.Name
    return data


def imprint(container: str, data: dict) -> bool:
    if not container:
        return False
    container_group = get_node_by_name(container)
    for key, value in data.items():
        target_param = container_group.PropertyList.Find(key)
        if target_param is None:
            container_group.PropertyCreate(key, FBPropertyType.kFBPT_charptr,
                                           value, False, True, None)
            target_param = container_group.PropertyList.Find(key)
            return True
        target_param.SetLocked(False)
        if isinstance(value, (dict, list)):
            target_param.Data = f"{JSON_PREFIX}{json.dumps(value)}"
        else:
            target_param.Data = value
        target_param.SetLocked(True)

    return True


def lsattr(
        attr: str,
        value: Union[str, None] = None,
        root: Union[str, None] = None) -> list:
    """List nodes having attribute with specified value.

    Args:
        attr (str): Attribute name to match.
        value (str, Optional): Value to match, of omitted, all nodes
            with specified attribute are returned no matter of value.
        root (str, Optional): Root node name. If omitted, scene root is used.

    Returns:
        list of nodes.
    """
    nodes = []
    for obj_sets in FBSystem().Scene.Sets:
        for prop in obj_sets.PropertyList:
            if value and prop.AsString() == value:
                nodes.append(obj_sets)
            elif prop.GetName() == attr:
                nodes.append(obj_sets)
    return nodes


def unique_namespace(namespace, format="%02d",
                     prefix="", suffix=""):
    """Return unique namespace

    Arguments:
        namespace (str): Name of namespace to consider
        format (str, optional): Formatting of the given iteration number
        suffix (str, optional): Only consider namespaces with this suffix.
        con_suffix: max only, for finding the name of the master container

    >>> unique_namespace("bar")
    # bar01
    >>> unique_namespace(":hello")
    # :hello01
    >>> unique_namespace("bar:", suffix="_NS")
    # bar01_NS:

    """

    def current_namespace():
        current = namespace
        # When inside a namespace Max adds no trailing :
        if not current.endswith(":"):
            current += ":"
        return current

    # Always check against the absolute namespace root
    # There's no clash with :x if we're defining namespace :a:x
    ROOT = ":" if namespace.startswith(":") else current_namespace()

    # Strip trailing `:` tokens since we might want to add a suffix
    start = ":" if namespace.startswith(":") else ""
    end = ":" if namespace.endswith(":") else ""
    namespace = namespace.strip(":")
    if ":" in namespace:
        # Split off any nesting that we don't uniqify anyway.
        parents, namespace = namespace.rsplit(":", 1)
        start += parents + ":"
        ROOT += start

    iteration = 1
    increment_version = True
    while increment_version:
        nr_namespace = namespace + format % iteration
        unique = prefix + nr_namespace + suffix
        cl = FBComponentList()
        FBFindObjectsByName((f"{unique}:*"), cl, True, True)
        if not cl:
            name_space = start + unique + end
            increment_version = False
            return name_space
        else:
            increment_version = True
        iteration += 1

def get_node_by_name(node_name: str):
    """Get instance node/container node by name

    Args:
        node_name (str): node name
    """
    matching_sets = [s for s in FBSystem().Scene.Sets
                        if s.Name == node_name]
    node = next(iter(matching_sets), None)
    return node


def get_selected_hierarchies(node, selection_data):
    """Get the hierarchies/children from the top group

    Args:
        node (FBObject): FBSystem().Scene.RootModel.Children
        selection_data (dict): data which stores the node selection
    """
    selected = True
    if node.ClassName() in {
        "FBModel", "FBModelSkeleton", "FBModelMarker",
        "FBCamera", "FBModelNull"}:
            if selection_data:
                for name in selection_data.keys():
                    if node.Name == name:
                        selected = selection_data[name]
            node.Selected = selected
    for child in node.Children:
        get_selected_hierarchies(child, selection_data)


def parsed_selected_hierarchies(node):
    """Parse the data to find the selected hierarchies
    Args:
        node (FBObject): FBSystem().Scene.RootModel.Children
    """
    selection_data = {}
    if node.ClassName() in {
        "FBModel", "FBModelSkeleton", "FBModelMarker",
        "FBCamera", "FBModelNull"}:
            selection_data[node.Name] = node.Selected
    for child in node.Children:
        parsed_selected_hierarchies(child)
    return selection_data


@contextlib.contextmanager
def maintain_selection(selected_nodes):
    """Maintain selection during context

    Args:
        selected_nodes (FBObject): selected nodes
    """
    if not selected_nodes:
        return
    selection_data = parsed_selected_hierarchies(selected_nodes)
    try:
        get_selected_hierarchies(selected_nodes, {})
        yield
    finally:
        get_selected_hierarchies(selected_nodes, selection_data)
