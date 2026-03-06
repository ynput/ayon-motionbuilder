from ayon_server.settings import BaseSettingsModel, SettingsField

from .create import CreatePluginsModel

DEFAULT_VALUES = {}


class MotionBuilderSettings(BaseSettingsModel):
    create: CreatePluginsModel = SettingsField(
        title="Create plugins",
        default_factory=CreatePluginsModel,
    )

