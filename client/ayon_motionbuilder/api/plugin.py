"""Motion Builder specific AYON/Pyblish plugin definitions."""
from abc import ABCMeta

import six

from ayon_core.lib import BoolDef
from ayon_core.pipeline import (
    CreatedInstance,
    Creator,
    CreatorError,
    AYON_INSTANCE_ID,
    AVALON_INSTANCE_ID,
)

from .lib import imprint, lsattr, read


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
            for prop in i.PropertyList:
                if prop.GetName() == "creator_identifier":
                    creator_id = prop.AsString()
                    if creator_id not in shared_data["mbuilder_cached_instances"]:
                        shared_data["mbuilder_cached_instances"][creator_id] = [i.Name]
                    else:
                        shared_data[
                            "mbuilder_cached_instances"][creator_id].append(i.name)
        return shared_data


