from ayon_server.settings import BaseSettingsModel, SettingsField


class MotionBuilderSettings(BaseSettingsModel):
    stop_timer_on_application_exit: bool = SettingsField(
        title="Stop timer on application exit")


DEFAULT_VALUES = {
    "stop_timer_on_application_exit": False
}
