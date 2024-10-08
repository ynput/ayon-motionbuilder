# -*- coding: utf-8 -*-
"""Pre-launch hook to inject python environment."""
import os
from ayon_applications import PreLaunchHook, LaunchTypes


class InjectPythonPath(PreLaunchHook):
    """Inject AYON environment to 3dsmax.

    Note that this works in combination whit 3dsmax startup script that
    is translating it back to PYTHONPATH for cases when 3dsmax drops PYTHONPATH
    environment.

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"motionbuilder"}
    launch_types = {LaunchTypes.local}

    def execute(self):
        self.launch_context.env["MOTIONBUILDER_PYTHON_STARTUP"] = os.environ["PYTHONPATH"]
