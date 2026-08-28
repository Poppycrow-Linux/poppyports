# TODO: organize!!
# # this is __init__ the module entry point. main() is defined here.
import argparse
import configparser
import hashlib
import os
import sys
import shlex
import shutil
import subprocess
import tarfile
import urllib.request

from .logutil import State, StateBenchmark, human_fsize


supressnonerrorlogs = False  # set as a global variable so the log function would Know
color = True  # same as above

# exceptions
class InvalidRecipeError(Exception):
  pass


class InvalidChecksumError(Exception):
  pass


# sam: I don't know what you just said but there HAS to be a better way to do this valera. #gotowork
#
# this one needs a bit of backstory
# argparse's store true or store false, quite obviously, returns false if not present or true if present
# however, this creates a problem where we cannot know when to fallback to the config, since false means that the option is just not present
# what if we generally want to ignore integrity errors, but not this time, for example?
# this class is an argparse action that makes the argument true if it is present at all or specified like --argument true
# if the value is absent, it returns none
# if it is explicitly set to false like --arg False, then it's false
# None means we fall back to config
class OptionalBoolAction(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    if values is None:
      setattr(namespace, self.dest, True)
      return

    v = str(values).lower()
    if v in {"true", "1", "yes", "on"}:
      setattr(namespace, self.dest, True)
    elif v in {"false", "0", "no", "off"}:
      setattr(namespace, self.dest, False)
    else:
      raise argparse.ArgumentTypeError(f"invalid boolean value for {option_string}: {values}")


# ANSI colors and printing
class Colors:
  ERROR = "\x1b[5;97;101m"
  WARNING = "\x1b[5;30;103m"
  SUCCESS = "\x1b[0;97;48;5;28m"
  SH_COMMAND = "\x1b[0;97;48;5;21m"
  END = "\x1b[0m"


def log(clr, *args):
  if (supressnonerrorlogs and (clr in {Colors.SUCCESS, Colors.ERROR, Colors.WARNING})) or not (supressnonerrorlogs):
    print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)


def quote(x):
  return shlex.quote(str(x))


def target_triple(arch, libc="glibc", vendor="crow"):
  if libc == "glibc":
    libc_suffix = "gnu"
  elif libc == "musl":
    libc_suffix = "musl"
  else:
    raise ValueError(f"unsupported libc: {libc}")

  if arch == "x86_64":
    return f"x86_64-{vendor}-linux-{libc_suffix}"
  if arch == "aarch64":
    return f"aarch64-{vendor}-linux-{libc_suffix}"
  if arch == "armv7":
    suffix = "gnueabihf" if libc == "glibc" else "musleabihf"
    return f"arm-{vendor}-linux-{suffix}"
  if arch == "i686":
    return f"i686-{vendor}-linux-{libc_suffix}"
  if arch == "riscv64":
    return f"riscv64-{vendor}-linux-{libc_suffix}"
  if arch == "ppc64le":
    return f"powerpc64le-{vendor}-linux-{libc_suffix}"
  if arch == "s390x":
    return f"s390x-{vendor}-linux-{libc_suffix}"

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


class BuildContext:  # https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
  ARCH = "x86_64"  # RUDE: fuck arm developer
  CFLAGS = ""  # "-Dick"
  CXXFLAGS = ""
  LDFLAGS = ""  # "-Dick2"
  SRCDIR = None  # this is package source directory
  PKGDIR = None  # this is package staging directory i.e. where it will be installed
  NPROC = 1
  SYSROOT = None
  SYSROOT_PATH = None
  SYSROOT_LOOKUP_DIR = None
  TARGET_DIR = None
  TOOLCHAIN = None
  TRIPLE = None
  TARGET = None
  LIBC = ""

  def __init__(self, builddir, portdir, recipe, sysroot=None, sysroot_path=None, toolchain=None, target=None):
    self.BUILDDIR = builddir
    self.PORTDIR = portdir
    self.SRCDIR = os.path.join(builddir, "pkgsrc")
    self.PKGDIR = os.path.join(builddir, "pkgdir")
    os.makedirs(self.SRCDIR, exist_ok=True)
    os.makedirs(self.PKGDIR, exist_ok=True)

    self.NPROC = os.cpu_count() or 1
    self.LIBC = "glibc"  # possible musl variant in the future TODO: package musl
    # i think this is wrong? ARCH would refer to our target architecture whereas recipe arch is the arch it can be built for
    # TODO: this should be replaced with if checks
    self.ARCH = recipe["arch"]
    self.TARGET = target or f"{self.ARCH}-{self.LIBC}"
    self.ARCH, self.LIBC = split_target(self.TARGET)
    self.recipe = recipe
    self.recipe["depends"] = [
      self.LIBC if pkg == "libc" else pkg for pkg in self.recipe["depends"]
    ]

    self.SYSROOT_LOOKUP_DIR = os.path.abspath(sysroot) if sysroot else None
    self.SYSROOT_PATH = os.path.abspath(sysroot_path) if sysroot_path else None
    self.TARGET_DIR = None
    self.SYSROOT = None
    self.TOOLCHAIN = os.path.abspath(toolchain) if toolchain else None
    self.TRIPLE = None
    self.CC = "cc"
    self.CXX = "c++"
    self.AR = "ar"
    self.RANLIB = "ranlib"
    self.STRIP = "strip"
    self.NM = "nm"

    if self.SYSROOT_PATH is None and self.SYSROOT_LOOKUP_DIR is not None:
      self.TARGET_DIR = os.path.join(self.SYSROOT_LOOKUP_DIR, self.TARGET)
      self.SYSROOT_PATH = os.path.join(self.TARGET_DIR, "sysroot")

    if self.SYSROOT_PATH is not None:
      self.SYSROOT = self.SYSROOT_PATH
      self.TRIPLE = target_triple(self.ARCH, self.LIBC)

      if self.TOOLCHAIN is None:
        if self.TARGET_DIR is not None:
          self.TOOLCHAIN = os.path.join(self.TARGET_DIR, "toolchain")
        else:
          self.TOOLCHAIN = os.path.join(os.path.dirname(self.SYSROOT), "toolchain")

      toolbindir = os.path.join(self.TOOLCHAIN, "bin")
      self.CC = os.path.join(toolbindir, f"{self.TRIPLE}-gcc")
      self.CXX = os.path.join(toolbindir, f"{self.TRIPLE}-g++")
      self.AR = os.path.join(toolbindir, f"{self.TRIPLE}-ar")
      self.RANLIB = os.path.join(toolbindir, f"{self.TRIPLE}-ranlib")
      self.STRIP = os.path.join(toolbindir, f"{self.TRIPLE}-strip")
      self.NM = os.path.join(toolbindir, f"{self.TRIPLE}-nm")

    self.env = self.make_build_environment()
    # self.env["DESTDIR"] = self.pkgdir
    # self.env["CFLAGS"] = self.CFLAGS

  def sh(self, *args, cwd=None, shell=False):
    if cwd is None: cwd = self.SRCDIR
    if len(args) == 1: shell = True

    # shell=True requires a string to be passed in i assume
    cmd = " ".join(args) if shell else args

    log(Colors.SH_COMMAND, f"+$ {' '.join(args) if isinstance(cmd, tuple) else cmd}")
    subprocess.run(cmd, cwd=cwd, env=self.env, check=True, shell=shell)

  def cp(self, frm, to):
    self.sh("cp", "-r", "-v", frm, to)

  def lnk(self, source, dest, relative=False, force=False):
    source = str(source)
    dest = str(dest)
    cwd = None
    if relative:
      cwd = os.path.abspath(os.path.dirname(dest) or ".")
      source = os.path.relpath(os.path.abspath(source), start=cwd)
    if force and os.path.lexists(dest):
      self.sh(f'rm -f -- {quote(dest)}', cwd=cwd)
    self.sh(f'ln -s -- {quote(source)} {quote(dest)}', cwd=cwd)

  def install_file(self, source, destination, mode=None):
    args = ["install", "-D", "-v"]
    if mode is not None: args += ["-m", str(mode)]
    self.sh(*args, source, destination)

  def install_dir(self, directory, mode="755"):
    self.sh("install", "-d", "-v", "-m", mode, directory)

  def apply_patches(self):
    patchdir = self.PORTDIR + "/patches"
    if not os.path.exists(patchdir): return  # no patches to apply
    for path, dirs, files in os.walk(patchdir):
      for patch in files:
        self.sh("patch", "-p1", "-i", f"{path}/{patch}")

  def chmod(self, mode, *paths):
    self.sh(f"chmod", mode, *paths)

  def build(self):
    self.recipe["build"](self)

  def write_cmake_toolchain(self):
    if self.SYSROOT is None:
      return None

    path = os.path.join(self.BUILDDIR, "pbuild-toolchain.cmake")

    with open(path, "w") as file:
      file.write(f"""\
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR {self.ARCH})

set(CMAKE_C_COMPILER {self.CC})
set(CMAKE_CXX_COMPILER {self.CXX})
set(CMAKE_AR {self.AR})
set(CMAKE_RANLIB {self.RANLIB})
set(CMAKE_STRIP {self.STRIP})

set(CMAKE_SYSROOT {self.SYSROOT})
set(CMAKE_FIND_ROOT_PATH {self.SYSROOT})

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
""")

    return path

  def install(self):
    self.recipe["install"](self)

  def make_build_environment(self):
    env = os.environ.copy()

    if self.SYSROOT is None:
      return env

    if self.SYSROOT_LOOKUP_DIR is not None and not os.path.isdir(self.SYSROOT_LOOKUP_DIR):
      raise InvalidRecipeError(f"sysroot lookup directory does not exist: {self.SYSROOT_LOOKUP_DIR}")

    if self.TARGET_DIR is not None and not os.path.isdir(self.TARGET_DIR):
      raise InvalidRecipeError(f"target directory does not exist: {self.TARGET_DIR}")

    if not os.path.isdir(self.SYSROOT):
      raise InvalidRecipeError(f"sysroot does not exist: {self.SYSROOT}")

    if not os.path.isdir(self.TOOLCHAIN):
      raise InvalidRecipeError(f"toolchain directory does not exist: {self.TOOLCHAIN}")

    toolbindir = os.path.join(self.TOOLCHAIN, "bin")
    if not os.path.isdir(toolbindir):
      raise InvalidRecipeError(f"toolchain bin directory does not exist: {toolbindir}")

    if not os.path.isfile(self.CC):
      raise InvalidRecipeError(f"cross compiler does not exist: {self.CC}")

    # These can cause host development files to leak into the build.
    for key in (
      "CPATH",
      "C_INCLUDE_PATH",
      "CPLUS_INCLUDE_PATH",
      "OBJC_INCLUDE_PATH",
      "LIBRARY_PATH",
      "PKG_CONFIG_PATH",
      "PKG_CONFIG_LIBDIR",
      "PKG_CONFIG_SYSROOT_DIR",
    ):
      env.pop(key, None)

    sysroot = self.SYSROOT

    pkgconfig_dirs = [
      os.path.join(sysroot, "usr", "lib", "pkgconfig"),
      os.path.join(sysroot, "usr", "lib64", "pkgconfig"),
      os.path.join(sysroot, "usr", "lib", self.TRIPLE, "pkgconfig"),
      os.path.join(sysroot, "usr", "share", "pkgconfig"),
      os.path.join(sysroot, "lib", "pkgconfig"),
      os.path.join(sysroot, "lib64", "pkgconfig"),
    ]

    env.update({
      "PATH": os.pathsep.join((toolbindir, env.get("PATH", ""))),
      "CC": self.CC,
      "CXX": self.CXX,
      "AR": self.AR,
      "RANLIB": self.RANLIB,
      "STRIP": self.STRIP,
      "NM": self.NM,

      "CPPFLAGS": f"--sysroot={sysroot}",
      "CFLAGS": f"--sysroot={sysroot} {self.CFLAGS}".strip(),
      "CXXFLAGS": f"--sysroot={sysroot} {self.CXXFLAGS}".strip(),
      "LDFLAGS": f"--sysroot={sysroot} {self.LDFLAGS}".strip(),

      # fuck over pkgconfig so it cannot look for path on the host
      "PKG_CONFIG_PATH": "",
      "PKG_CONFIG_LIBDIR": os.pathsep.join(pkgconfig_dirs),
      "PKG_CONFIG_SYSROOT_DIR": sysroot,

      # some makefiles understand it
      "CROSS_COMPILE": self.TRIPLE + "-",

      # no more setting destdir manually
      "DESTDIR": self.PKGDIR,

      "CMAKE_TOOLCHAIN_FILE": self.write_cmake_toolchain(),
    })

    return env


def read_recipe(path):
  with open(path, "r") as f:
    recipe_def = {}
    exec(f.read(), recipe_def)

    REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"}
    missing_keys = REQUIRED_KEYS - recipe_def.keys()  # this is set subtraction
    if missing_keys:
      raise InvalidRecipeError(f"This recipe is missing the {', '.join(missing_keys)} key(s)!")
    return recipe_def


def download_files(ctx, recipe, redownload):
  skip_extracting = False
  for url in recipe["sources"]:
    if url.startswith("https://") and not url.endswith(".git"):
      # TODO: download progress logging. use urllib to stream to a file directly in chunks and compute progress from this
      filename = url.split("/")[-1]
      dest = f"{ctx.BUILDDIR}/{filename}"
      if not os.path.exists(dest) or redownload:
        log(None, f"Downloading {url} to {dest}")
        urllib.request.urlretrieve(url, dest)
      else:
        log(None, f"{dest} already exists, skipping download!")

    elif url.startswith("git://"):
      # new TODO: remove this entirely. we should probably never clone directly from git this is a pretty bad idea in general for patches versioning and everything
      skip_extracting = True
      dest = f"{ctx.SRCDIR}/{recipe['pkgname']}"
      if not os.path.exists(dest) or redownload:
        log(None, f"Cloning {url} to {dest} via git")
        ctx.sh("git", "clone", "--depth", "1", url, dest)
      else:
        log(None, f"{dest} already exists, skipping download!")

  return skip_extracting


def calc_checksum(path, algorithm="sha256"):
  hasher = hashlib.new(algorithm)
  with open(path, "rb") as file:
    while chunk := file.read(8192):
      hasher.update(chunk)
  return hasher.hexdigest()


def check_downloaded(ctx, recipe):
  successes = []
  files = []
  fails = []
  i = 0
  for url in recipe["sources"]:
    filename = url.split("/")[-1]
    dest = f"{ctx.BUILDDIR}/{filename}"
    files.append(dest)
    successes.append(calc_checksum(dest) == recipe["sha256sum"][i])
  if not (False in successes):
    return True
  else:
    for i in range(len(files)):
      if not (successes[i]):
        fails.append(files[i])
    return fails


def extract_src(ctx, recipe):
  for url in recipe["sources"]:
    # TODO: skip extraction if already extracted (?)
    filename = url.split("/")[-1]
    dest = f"{ctx.BUILDDIR}/{filename}"
    with tarfile.open(dest, "r") as f:
      f.extractall(ctx.SRCDIR)


def main():
  parser = argparse.ArgumentParser(
    prog="pbuild",
    description="Compiles apk files to be used in Poppycrow Linux repos.",
    epilog="See more @ https://codeberg.org/Poppycrow-Linux/poppyports",
  )
  parser.add_argument(
    "pkgpath", help="Path of the folder that contains the build recipe."
  )
  parser.add_argument(
    "-ignoreintegrity",
    "-ii",
    "-ignore-broken-files",
    action=OptionalBoolAction,
    help="Ignore any checksum errors and continue building the package.",
    nargs="?",
  )
  parser.add_argument(
    "-fresh",
    "-new",
    "-redownload",
    action=OptionalBoolAction,
    help="Redownload files even if they are already present and pass the integrity checks.",
    nargs="?",
  )
  parser.add_argument(
    "-rebuild",
    action=OptionalBoolAction,
    help="Force rebuild even when package is already built.",
    nargs="?",
  )
  parser.add_argument(
    "-color",
    action=OptionalBoolAction,
    help="Highlight warnings, errors and build completion.",
    nargs="?",
  )
  parser.add_argument(
    "-buildstatebreakdown",
    "-bsbd",
    "-bb",
    action=OptionalBoolAction,
    help="Show build state breakdown.",
    nargs="?",
  )
  parser.add_argument(
    "-supressnonerrorlogs",
    "-clean-logs",
    action=OptionalBoolAction,
    help="Supress logs that aren't warnings, errors, or completion messages",
    nargs="?",
  )
  parser.add_argument(
    "builddir", help="The directory to build the recipe in.", nargs="?"
  )
  parser.add_argument("-config", help="The config to use.", nargs="?")
  parser.add_argument("-portsdir", help="Folder with ports in it.", nargs="?")
  parser.add_argument("-target", help="Target in ARCH-LIBC form, for example aarch64-glibc.", nargs="?")
  parser.add_argument("-sysroot", help="Directory containing per-target sysroot folders.", nargs="?")
  parser.add_argument("-sysrootpath", "-sysroot-path", help="Specific target sysroot directory.", nargs="?")
  parser.add_argument("-toolchain", help="Specific cross-toolchain directory.", nargs="?")
  parser.add_argument(
    "-appendportsdirtopath",
    "-apd",
    action=OptionalBoolAction,
    help="Appends the ports directory to the path of the recipe to build. Defaults to true, so syntax like pbuild main/linux-stable continues to work.",
    nargs="?",
  )
  parser.add_argument(
    "-signkey", help="Signature private key to use for apk signing", nargs="?"
  )
  args = parser.parse_args()

  CONFIGFILEPATH = "./pbuild.conf"
  if args.config:  # parse configfilepath earlier than the rest so we can override it
    CONFIGFILEPATH = args.config

  # fallback variables
  appendportsdirtopath = True
  portsdir = "./recipes"
  ignoreintegrity = False
  color = True
  rebuild = False
  show_bs_breakdown = True
  supressnonerrorlogs = False
  target = None
  sysroot = None
  sysroot_path = None
  toolchain = None

  # TODO: move config reading to a separate function

  cfgparser = configparser.ConfigParser()
  cfgparser.read(CONFIGFILEPATH)
  if cfgparser.sections() == []:
    cfgparser["Build"] = {
      "AssumeRebuild": "no",
      "AssumeRedownload": "no",
      "DefaultBuildPath": "./build",
      "AssumeRebuild": "no",
      "AssumeIgnoreIntegrity": "no",
      "PortsPath": "./recipes",
      "AppendPortsPathToRecipePath": "yes",
      "Target": "",
      "Sysroot": "",
      "SysrootPath": "",
      "Toolchain": "",
    }
    cfgparser["Display"] = {
      "Color": "yes",
      "SupressNonErrorLogs": "no",
      "BuildStateBreakdown": "yes",
    }
    configfile = open(CONFIGFILEPATH, "w")

  if os.path.getsize(CONFIGFILEPATH) == 0:
    ## TODO: write default config sections if missing. maybe not needed (question Mark), since the defaults are kind of above
    cfgparser.write(configfile)

  appendportsdirtopath = cfgparser.getboolean("Build", "AppendPortsPathToRecipePath")
  ignoreintegrity = cfgparser.getboolean("Build", "AssumeIgnoreIntegrity")
  redownload = cfgparser.getboolean("Build", "AssumeRedownload")
  builddir = cfgparser["Build"]["DefaultBuildPath"]
  target = cfgparser.get("Build", "Target", fallback="")
  sysroot = cfgparser.get("Build", "Sysroot", fallback="")
  sysroot_path = cfgparser.get("Build", "SysrootPath", fallback="")
  toolchain = cfgparser.get("Build", "Toolchain", fallback="")
  color = cfgparser.getboolean("Display", "Color")
  supressnonerrorlogs = cfgparser.getboolean("Display", "SupressNonErrorLogs")
  rebuild = cfgparser.getboolean("Build", "AssumeRebuild")
  show_bs_breakdown = cfgparser.getboolean("Display", "BuildStateBreakdown")

  if args.appendportsdirtopath is not None:
    appendportsdirtopath = args.appendportsdirtopath
  if args.pkgpath is not None:
    pkgpath = args.pkgpath  # ifs added so that cmdline functions cannot override shit when they are not set
  if args.ignoreintegrity is not None:
    ignoreintegrity = args.ignoreintegrity
  if args.builddir is not None:
    builddir = args.builddir
  if args.target is not None:
    target = args.target
  if args.sysroot is not None:
    sysroot = args.sysroot
  if args.sysrootpath is not None:
    sysroot_path = args.sysrootpath
  if args.toolchain is not None:
    toolchain = args.toolchain
  if args.color is not None:
    color = args.color
  if args.fresh is not None:
    redownload = args.fresh
  if args.supressnonerrorlogs is not None:
    supressnonerrorlogs = args.supressnonerrorlogs
  if args.rebuild is not None:
    rebuild = args.rebuild
  if args.buildstatebreakdown is not None:
    show_bs_breakdown = args.buildstatebreakdown

  if not target:
    target = None
  if not sysroot:
    sysroot = None
  if not sysroot_path:
    sysroot_path = None
  if not toolchain:
    toolchain = None

  # pkgpath = sys.argv[1]
  # builddir = sys.argv[2]

  # SCRIPT BEGINNING, MOVE THIS SOMEWHERE!!!
  bench = StateBenchmark()

  log(None, f"Arguments used: {args}")

  if appendportsdirtopath:
    pkgpath_real = f"{portsdir}/{pkgpath}"
  else:
    pkgpath_real = pkgpath

  recipe = read_recipe(f"{pkgpath_real}/recipe.py")

  ctx = BuildContext(os.path.abspath(builddir), os.path.abspath(pkgpath_real), recipe, sysroot, sysroot_path, toolchain, target)
  log(None, f"NPROC: {ctx.NPROC}")

  if ctx.SYSROOT is not None:
    log(None, f"Target: {ctx.TARGET}")
    if ctx.SYSROOT_LOOKUP_DIR is not None:
      log(None, f"Sysroot lookup directory: {ctx.SYSROOT_LOOKUP_DIR}")
    if ctx.TARGET_DIR is not None:
      log(None, f"Target directory: {ctx.TARGET_DIR}")
    log(None, f"Resolved sysroot: {ctx.SYSROOT}")
    log(None, f"Toolchain: {ctx.TOOLCHAIN}")
    log(None, f"Cross compiler: {ctx.CC}")

  # ok so normally I would make this a config option but removing the pkgdir is neccesary to avoid
  # accidentally including the leftover files from unsuccessful builds.
  os.makedirs(ctx.BUILDDIR, exist_ok=True)

  outpath = f"{builddir}/{recipe['pkgname']}-{recipe['pkgver']}.apk"
  if os.path.exists(outpath) and not rebuild:
    log(Colors.WARNING, f"Skipping build as {outpath} already exists. If you need to rebuild, pass the -rebuild flag to force rebuilding.")
    sys.exit(0)

  if redownload and os.path.exists(ctx.SRCDIR):
    log(Colors.SH_COMMAND, f"Removing {ctx.SRCDIR} as redownload flag has been passed!")
    shutil.rmtree(ctx.SRCDIR)

  bench.change(State.DOWNLOAD)
  log(None, "Downloading files")
  skip_extracting = download_files(ctx, recipe, redownload)

  if "sha256sum" in recipe:
    bench.change(State.CHECKSUM)
    log(None, "Checksum found in recipe, checking...")

    if check_downloaded(ctx, recipe) == True:
      log(Colors.SUCCESS, "☑ Integrity check passed.")
    else:
      log(Colors.ERROR, "!!!!!!!!!!!! INTEGRITY CHECK FAILED !!!!!!!!!!!!")
      log(Colors.ERROR, check_downloaded(ctx, recipe), " FAILED THE CHECKSUM")
      if not ignoreintegrity:
        raise InvalidChecksumError("One or more file(s) did not pass the integrity check. Use -ii or -ignoreintegrity to bypass this error.")
  else:
    log(Colors.WARNING, f"//// SHA256 checksum not found in recipe {recipe['pkgname']}, extracting without checks. ////")

  bench.change(State.EXTRACT)
  if not skip_extracting:
    if os.path.exists(ctx.PKGDIR):
      shutil.rmtree(ctx.PKGDIR)
      log(Colors.SH_COMMAND, f"Removing {ctx.PKGDIR}")

    log(None, "Extracting source...")
    extract_src(ctx, recipe)

  log(None, "Building...")
  bench.change(State.BUILD)
  ctx.build()
  bench.change(State.INSTALL)
  ctx.install()

  # make apk
  # TODO: at the top of main(), run a preflight() to check if apk and various other important things are available.
  # TODO: move all apk related operations to its own module.
  def run_apk(args):
    # env = os.environ.copy()
    # env["LD_LIBRARY_PATH"] = "staging/apk-install/lib/x86_64-linux-gnu/"
    subprocess.run(["apk"] + list(args), env=os.environ, check=True)

  # TODO: https://man.archlinux.org/man/apk-package.5.en
  apkcmd = ["mkpkg"]
  if args.signkey:
    apkcmd.extend(["--sign-key", args.signkey])

  # somebody pls figure this shit out i am so done
  depends = []
  for p in recipe["depends"]:
    depends.append(p)

  apkcmd.extend([
    "-I", f"name:{recipe['pkgname']}",
    "-I", f"version:{recipe['pkgver']}",
    "-I", f"description:{recipe['pkgdesc']}",
    "-I", f"arch:{ctx.ARCH}",
    "-I", f"license:{recipe['license']}",
    "-I", f"url:{recipe['url']}",
    "-I", f"depends:{' '.join(depends)}",
  ])
  apkcmd.extend(["-F", ctx.PKGDIR, "-o", outpath])

  run_apk(apkcmd)

  bench.change(State.DONE)
  log(Colors.SUCCESS, f"Done! Generated {outpath} ({human_fsize(outpath)})")
  if show_bs_breakdown:
    print()
    log(Colors.SUCCESS, f"Build Breakdown")
    print()
    print(bench.build_breakdown())
