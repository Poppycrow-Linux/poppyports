import os
import tempfile
import shutil
import subprocess
from .logutil import Colors, InvalidRecipeError, log

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

## TODO: the kernel arches among with other things should be declared in some sort of target config.
## see how chimera does it: https://github.com/chimera-linux/cports/tree/master/etc/build_profiles
## this could probably also be improved by moving the kernel arches and whatnot here
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

def write_meson_cross_file(sysroot, builddir, cc, cxx, ar, strip, arch): # this isn't really used anywhere even though it really should
  if sysroot is None:
    return None

  path = os.path.join(builddir, "pbuild-meson-cross.ini")

  with open(path, "w") as file:
    file.write(f"""\
[binaries]
c = '{cc}'
cpp = '{cxx}'
ar = '{ar}'
strip = '{strip}'
pkg-config = 'pkgconf'

[properties]
sys_root = '{sysroot}'
needs_exe_wrapper = true

[host_machine]
system = 'linux'
cpu_family = '{arch}'
cpu = '{arch}'
endian = 'little'
""")
  print("written meson cross file to", path)
  return path

def install_to_cache(pkgdir: str, libs_root: str, target: str, pkgname: str, pkgver: str) -> str:
    pkg_cache = os.path.join(libs_root, target, f"{pkgname}-{pkgver}")
    if os.path.exists(pkg_cache):
        shutil.rmtree(pkg_cache)
    shutil.copytree(pkgdir, pkg_cache)
    return pkg_cache



def compose_sysroot(base_sysroot: str, libs_root: str, target: str, deps: list[str]) -> str:
    overlay_dir = tempfile.mkdtemp(prefix="overlay-")
    composed_dir = tempfile.mkdtemp(prefix="sysroot-")

    # Merge selected packages into overlay_dir
    for pkg in deps:
        pkg_path = os.path.join(libs_root, target, pkg)
        if not os.path.isdir(pkg_path):
            print(f"Package not found in cache: {pkg_path}, but it might not be a library, so we barrel along.")
            continue
        for entry in os.listdir(pkg_path):
            print(entry)
            src = os.path.join(pkg_path, entry)
            dst = os.path.join(overlay_dir, entry)
            if os.path.isdir(src):
                print(f"Copying {src} to {dst}")
                shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
            else:
                print(f"Copying {src} to {dst}")
                shutil.copy2(src, dst)

    # Start from base sysroot
    for entry in os.listdir(base_sysroot):
        src = os.path.join(base_sysroot, entry)
        dst = os.path.join(composed_dir, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
        else:
            shutil.copy2(src, dst)

    # Overlay package files on top
    for entry in os.listdir(overlay_dir):
        src = os.path.join(overlay_dir, entry)
        dst = os.path.join(composed_dir, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
            print(f"Copying {src} to {dst}")
        else:
            shutil.copy2(src, dst)
            print(f"Copying {src} to {dst}")
    # while True: pass
    return composed_dir

import tempfile

def _try_kernel_overlay(lowers, upper, work, merged):
    opts = "lowerdir=" + ":".join(lowers) + f",upperdir={upper},workdir={work}"
    r = subprocess.run(
        ["mount", "-t", "overlay", "overlay", "-o", opts, merged],
        capture_output=True,
    )
    return r.returncode == 0


def _try_fuse_overlay(lowers, upper, work, merged):
    # requires the `fuse-overlayfs` binary on PATH (or the python wrapper)
    cmd = ["fuse-overlayfs", "-o",
           "lowerdir=" + ":".join(lowers) + f",upperdir={upper},workdir={work}",
           merged]
    try:
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def compose_sysroot_overlay(base_sysroot, libs_root, target, deps):
    lowers = []
    for dep in deps:
        p = f"{libs_root}/{target}/{dep}"
        if os.path.isdir(p):
            lowers.append(p)
        else:
            log(Colors.WARNING, f"missing lib dir: {p}")
    lowers.append(base_sysroot)

    tmp = tempfile.mkdtemp(prefix="pbuild-overlay-")
    upper = os.path.join(tmp, "upper")
    work  = os.path.join(tmp, "work")
    merged = os.path.join(tmp, "merged")
    for d in (upper, work, merged):
        os.makedirs(d)

    if _try_kernel_overlay(lowers, upper, work, merged):
        backend = "kernel-overlayfs"
    elif _try_fuse_overlay(lowers, upper, work, merged):
        backend = "fuse-overlayfs"
    else:
        shutil.rmtree(tmp, ignore_errors=True)
        return None  # caller falls back to compose_sysroot()

    log(Colors.SUCCESS, f"composed sysroot via {backend}: {merged}")
    return {
        "merged": merged,
        "tmp": tmp,
        "backend": backend,
    }


def teardown_overlay(state):
    if not state:
        return
    log(Colors.SH_COMMAND, f"Tearing down overlay {state["tmp"]}")
    subprocess.run(["umount", "-l", state["merged"]],
                   capture_output=True)
    shutil.rmtree(state["tmp"], ignore_errors=True)
