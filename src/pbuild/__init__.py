# TODO: organize!!
# # this is __init__ the module entry point. main() is defined here.
import argparse
import itertools
import configparser
import hashlib
import os
import sys
import shlex
import shutil
import subprocess
import tarfile
import urllib.request
import platform
from dataclasses import dataclass, field


from .buildcontext import BuildContext
from .logutil import State, StateBenchmark, human_fsize, Colors, InvalidRecipeError, InvalidChecksumError
from .config import load_config
from .crossutils import install_to_cache, compose_sysroot

def log(clr, *args):
  if (supressnonerrorlogs and (clr in important_colors)) or not (supressnonerrorlogs):
    print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)

supressnonerrorlogs = False  # set as a global variable so the log function would Know
color = True  # same as above

def log(clr, *args):
  if (supressnonerrorlogs and (clr in important_colors)) or not (supressnonerrorlogs):
    print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)

# exceptions



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


def log(clr, *args):
  if (supressnonerrorlogs and (clr in {Colors.SUCCESS, Colors.ERROR, Colors.WARNING})) or not (supressnonerrorlogs):
    print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)


def quote(x):
  return shlex.quote(str(x))

def read_recipe(path):
  with open(path, "r") as f:
    recipe_def = {}
    exec(f.read(), recipe_def)

    REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"}
    missing_keys = REQUIRED_KEYS - recipe_def.keys()  # this is set subtraction
    if missing_keys:
      pass
      # raise InvalidRecipeError(f"This recipe is missing the {', '.join(missing_keys)} key(s)!")
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
  parser = argparse.ArgumentParser(prog="pbuild",
    description="Compiles apk files to be used in Poppycrow Linux repos.",
    epilog="See more @ https://codeberg.org/Poppycrow-Linux/poppyports",)
  parser.add_argument("pkgpath", help="Path of the folder that contains the build recipe.")
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
  parser.add_argument("-lib", "-install-as-lib", action=OptionalBoolAction,
    help="Caches the contents of PKGDIR into /{BUILDDIR}}/{TARGET}/{pkgname}, which is then used for overlaying libs on top of sysroot",
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
  parser.add_argument("-signkey", help="Signature private key to use for apk signing", nargs="?")
  parser.add_argument("-libs-root", help="Path to look for cross-compiled libraries in.", nargs="?")
  args = parser.parse_args()
  CONFIGFILEPATH = args.config if args.config else "./pbuild.conf"
  cfg = load_config(CONFIGFILEPATH, args)
  globals().update(vars(cfg)) # this is a trick to unpack a class into global namespace. it can overwrite variables but I could not give less of a fuck
  # SCRIPT BEGINNING, MOVE THIS SOMEWHERE!!!
  bench = StateBenchmark()

  log(None, f"Arguments used: {args}")

  if append_portsdir:
    pkgpath_real = f"{portsdir}/{pkgpath}"
  else:
    pkgpath_real = pkgpath

  recipe = read_recipe(f"{pkgpath_real}/recipe.py")

  ctx = BuildContext(os.path.abspath(builddir), os.path.abspath(pkgpath_real), recipe, sysroot, sysroot_path, toolchain, target)
  ctx.LIBS_ROOT = libs_root
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
  if rebuild and os.path.exists(ctx.PKGDIR):
    log(Colors.SH_COMMAND, f"Removing {ctx.PKGDIR}")
    shutil.rmtree(ctx.PKGDIR)
  os.makedirs(ctx.BUILDDIR, exist_ok=True)
  os.makedirs(ctx.PKGDIR, exist_ok=True)
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

  os.makedirs(ctx.PKGDIR, exist_ok=True)


  if ctx.SYSROOT and recipe["depends"]:
    log(Colors.SH_COMMAND, "Making a sysroot with needed libraries!")
    dependencies = []
    for j in recipe["depends"]: dependencies.append(j)
    if "makedepends" in recipe.keys():
      for j in recipe["makedepends"]:
        if os.path.exists("portsdir" + f"/main/{j}/recipe.py"):
          dependencies.append(j)
        else:
          log(Colors.WARNING, f"{portsdir}/main/{j}/recipe.py DOES NOT EXIST!!")
    versions = []
    for i in dependencies:
      if os.path.exists("portsdir" + f"/main/{i}/recipe.py"):
        k = read_recipe(portsdir + f"/main/{i}/recipe.py")
        versions.append(k["pkgver"])

    composed = compose_sysroot(
          base_sysroot = ctx.SYSROOT,
          libs_root = cfg.libs_root,
          target = ctx.TARGET,
          deps=[f"{pkg}-{ver}" for pkg, ver in zip(dependencies, versions)],
      )
    ctx.SYSROOT = composed
    log(Colors.SUCCESS, f"Made sysroot: {composed}")
    ctx._composed_sysroot = composed  # for later cleanup
  log(None, "Building...")
  bench.change(State.BUILD)
  ctx.build()
  bench.change(State.INSTALL)
  ctx.install()
  if lib:
    log(Colors.SH_COMMAND, f"Installing library to {ctx.LIBS_ROOT}")
    install_to_cache(ctx.PKGDIR, ctx.LIBS_ROOT, ctx.TARGET, recipe["pkgname"], recipe["pkgver"])


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
  if show_build_breakdown:
    print()
    log(Colors.SUCCESS, f"Build Breakdown")
    print()
    print(bench.build_breakdown())
    if hasattr(ctx, "_composed_sysroot") and ctx._composed_sysroot is not None:
      log(Colors.SH_COMMAND, f"Removing {ctx._composed_sysroot}")
      shutil.rmtree(ctx._composed_sysroot, ignore_errors=True)
