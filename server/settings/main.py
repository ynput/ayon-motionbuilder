from ayon_server.settings import BaseSettingsModel, SettingsField


class MotionBuilderSettings(BaseSettingsModel):
    workfile_test: bool = SettingsField(
        title="Workfile Test")


DEFAULT_VALUES = {
    "workfile_test": False
}
