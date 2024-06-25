from ayon_motionbuilder.api import plugin


class CreateAnimation(plugin.MotionBuilderCreator):
    """Fbx for animated data"""

    identifier = "io.ayon.creators.motionbuilder.animation"
    label = "Animation"
    product_type = "animation"
    icon = "gears"
