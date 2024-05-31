# -*- coding: utf-8 -*-
"""Pre-launch to force motion builder startup script."""
import os
from ayon_motionbuilder import MOTION_BUILDER_HOST_DIR
from ayon_applications import PreLaunchHook, LaunchTypes


class ForceStartupScript(PreLaunchHook):
    """Inject AYON environment to motion builder.

    Note that this works in combination whit motion builder startup script that
    is translating it back to PYTHONPATH for cases when motion builder drops PYTHONPATH
    environment.

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"motionbuilder"}
    order = 11
    launch_types = {LaunchTypes.local}

    def execute(self):
        startup_args = [
            "-suspendMessages",
            os.path.join(MOTION_BUILDER_HOST_DIR, "startup", "startup.py"),
        ]
        self.launch_context.launch_args.append(startup_args)