# -*- coding: utf-8 -*-
import os
from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__


MOTION_BUILDER_ADDON_ROOT = os.path.dirname(
    os.path.abspath(__file__))


class MotionBuilderAddon(AYONAddon, IHostAddon):
    name = "motionbuilder"
    version = __version__
    host_name = "motionbuilder"

    def add_implementation_envs(self, env, _app):
        # Remove auto screen scale factor for Qt
        env.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)

    def get_workfile_extensions(self):
        return [".fbx"]

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(MOTION_BUILDER_ADDON_ROOT, "hooks")
        ]
