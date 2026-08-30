# this is where the buildstyles are registered. this is done to avoid importing everything
# in pbuild, so anything that could need buildstyles can just import them

# from .cmake import CMakeStyle
from .gnu_configure import GnuConfigureStyle
from .makefile import MakefileStyle
from .meson import MesonStyle
from .kernel import KernelStyle
from .kernel_headers import KernelHeadersStyle


BUILD_STYLES = {
  #"cmake": CMakeStyle, todo: add the cmake style
  "gnu_configure": GnuConfigureStyle,
  "makefile": MakefileStyle,
  "meson": MesonStyle,
  "kernel": KernelStyle,
  "kernel_headers": KernelHeadersStyle,
}


def get_build_style(name, context):
  try:
    return BUILD_STYLES[name](context)
  except KeyError as error:
    raise ValueError(f"unknown build style: {name}") from error
