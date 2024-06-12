
import pyblish.api
from ayon_core.lib import BoolDef


class CollectAnimationFamily(pyblish.api.InstancePlugin):
    label = "Collect Animation Family"
    order = pyblish.api.CollectorOrder - 0.4
    hosts = ["motionbuilder"]

    def process(self, instance):
        attr_values = self.get_attr_values_from_data(instance.data)
        if not attr_values.get("animation_family"):
            self.log.debug(
                "Skipping to publish instance to animation family.")
            return

        instance.data["families"].append("animation")

    @classmethod
    def get_attribute_defs(cls):
        return [
            BoolDef("animation_family",
                    label="Add Animation family",
                    default=True)
        ]
