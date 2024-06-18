# -*- coding: utf-8 -*-
import pyblish.api
from ayon_core.pipeline import PublishValidationError
from pyfbsdk import FBApplication


class ValidateSceneSaved(pyblish.api.InstancePlugin):
    """Validate that workfile was saved."""

    order = pyblish.api.ValidatorOrder
    families = ["workfile"]
    hosts = ["motionbuilder"]
    label = "Validate Workfile is saved"

    def process(self, instance):
        if not FBApplication().FBXFileName:
            raise PublishValidationError(
                "Workfile is not saved", title=self.label)
