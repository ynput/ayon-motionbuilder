import contextlib
import logging
import json
from typing import Any, Dict, Union

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
    print(data)
    return data


def imprint(container:str, data: dict) -> bool:
    if not container:
        return False
    container_group = next(
        (obj_set for obj_set in FBSystem().Scene.Sets
         if obj_set.Name == container), None)
    for key, value in data.items():
        target_param = container_group.PropertyList.Find(key)
        if not target_param:
            container_group.PropertyCreate(
                key, FBPropertyType.kFBPT_charptr,
                value, False, True, None)

        target_param.SetLocked(False)
        target_param.Data = value
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
                     prefix="", suffix="", con_suffix="CON"):
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
