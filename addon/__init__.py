from . import utils
from . import props
from . import icons
from . import ops
from . import ui


def register():
    utils.register()
    props.register()
    icons.register()
    ops.register()
    ui.register()


def unregister():
    ui.unregister()
    ops.unregister()
    props.unregister()
    icons.unregister()
    utils.unregister()
