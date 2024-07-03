import traceback

import contextlib
import pyblish.util
from pyfbsdk import FBSystem
from ayon_core.pipeline import (
    registered_host
)
from ayon_core.pipeline.create import CreateContext

from . import lib
from ayon_motionbuilder.api.lib import get_node_by_name

# Needed for transition phase for asset/subset renaming. Can be hardcoded once
# transition is done.
product_key_name = "productName"
product_type_key_name = "productType"


def test_create():
    """Test re-creating instances in workfile.
    """

    host = registered_host()
    context = CreateContext(host)
    data = {
        "creator_identifier": "io.ayon.creators.motionbuilder.animation",
        "creator_attributes": {
            "EmbedMedia": True,
            "SaveSelectedModelsOnly": True,
            "KeepTransformHierarchy": True
        }
    }
    with select_model():
        created_instance = context.create(
            creator_identifier=data["creator_identifier"],
            variant="Test",
            pre_create_data={"use_selection": True}
        )
        if created_instance:
            for key, value in data["creator_attributes"].items():
                created_instance.creator_attributes[key] = value

        context.save_changes()
    print("Create was successful!")


@contextlib.contextmanager
def select_model():
    original_selection = {}
    for component in FBSystem().Scene.Components:
        original_selection.update({component.Name: component.Selected})
    try:
        for component in FBSystem().Scene.Components:
            component.Selected = True
        yield
    finally:
        for key, value in original_selection.items():
            node = get_node_by_name(key)
            node.Selected = value
