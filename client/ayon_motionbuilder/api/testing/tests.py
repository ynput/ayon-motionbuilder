import contextlib
import pyblish.util
from pyfbsdk import FBSystem
from ayon_core.pipeline import (
    registered_host
)
from ayon_core.pipeline.create import CreateContext

from . import lib


def test_create_animation():
    """Test re-creating instances in workfile.
    """

    host = registered_host()
    context = CreateContext(host)
    # TODO: replace the hardcoded of the data
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

    print("Create was successful!")


def test_publish_animation():
    """Test Publishing
    """
    context = pyblish.util.publish()
    success = True
    for result in context.data["results"]:
        if not result["success"]:
            success = False
            break

    assert success, lib.create_error_report(context)

    print("Publish was successful!")


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
        for component in FBSystem().Scene.Components:
            for key, value in original_selection.items():
                if component.Name == key:
                        component.Selected = value