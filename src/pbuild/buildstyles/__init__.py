# from .cmake import CMakeStyle
from .gnu_configure import GnuConfigureStyle
from .makefile import MakefileStyle
from .meson import MesonStyle


BUILD_STYLES = {
  #"cmake": CMakeStyle, todo: add the cmake style
  "gnu_configure": GnuConfigureStyle,
  "makefile": MakefileStyle,
  "meson": MesonStyle,
}


def get_build_style(name, context):
  try:
    return BUILD_STYLES[name](context)
  except KeyError as error:
    raise ValueError(f"unknown build style: {name}") from error
