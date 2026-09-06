import os

def target_triple(arch, libc="glibc", vendor="crow"):
  idiot_arches = ["armv7", "gnueabihf", "ppc64le", 'powerpc64le']
  if libc == "glibc": libc_suffix = "gnu"
  else: libc_suffix = libc # it works for musl and I do not care enough for others
  if arch not in idiot_arches:
     return f"{arch}-{vendor}-linux-{libc_suffix}"
  if arch == "armv7" or "gnueabihf":
    libc_suffix += "eabihf" # works for musl and glibc.
    return f"arm-{vendor}-linux-{libc_suffix}"
  if arch == "ppc64le" or "powerpc64le":
    return f"powerpc64le-{vendor}-linux-{libc_suffix}"

  raise ValueError(f"unsupported target architecture: {arch}")


def split_target(target):
  try:
    arch, libc = target.rsplit("-", 1)
  except ValueError as error:
    raise InvalidRecipeError(f"invalid target: {target}; expected ARCH-LIBC") from error

  try:
    target_triple(arch, libc)
  except ValueError as error:
    raise InvalidRecipeError(str(error)) from error

  return arch, libc

KERNEL_ARCHES = {
  "x86_64": "x86",
  "aarch64": "arm64",
  "armv7": "arm",
  "i686": "x86",
  "riscv64": "riscv",
  "ppc64le": "powerpc",
  "s390x": "s390",
}

def write_cmake_toolchain(SYSROOT, BUILDDIR, ARCH, CC, CXX, AR, RANLIB, STRIP):
  if SYSROOT is None:
    return None

  path = os.path.join(BUILDDIR, "pbuild-toolchain.cmake")

  with open(path, "w") as file:
    file.write(f"""\
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR {ARCH})

set(CMAKE_C_COMPILER {CC})
set(CMAKE_CXX_COMPILER {CXX})
set(CMAKE_AR {AR})
set(CMAKE_RANLIB {RANLIB})
set(CMAKE_STRIP {STRIP})

set(CMAKE_SYSROOT {SYSROOT})
set(CMAKE_FIND_ROOT_PATH {SYSROOT})

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
""")

  return path

def write_meson_cross_file(self): # this isn't really used anywhere even though it really should
  if self.SYSROOT is None:
    return None

  path = os.path.join(self.BUILDDIR, "pbuild-meson-cross.ini")

  with open(path, "w") as file:
    file.write(f"""\
[binaries]
c = '{self.CC}'
cpp = '{self.CXX}'
ar = '{self.AR}'
strip = '{self.STRIP}'
pkgconfig = 'pkg-config'

[properties]
sys_root = '{self.SYSROOT}'
needs_exe_wrapper = true

[host_machine]
system = 'linux'
cpu_family = '{self.ARCH}'
cpu = '{self.ARCH}'
endian = 'little'
""")

  return path
