# hi this is staging build system prototyping bullshit rn this is how you do apk
# i need to clean up - sam
# TODO: handle depends and also like basically redo what chimera and APKBUILDs do
# TODO: Everything.
# hi sam
import os
import sys
import io
import subprocess
import urllib.request
import tarfile
import hashlib
import argparse
from enum import Enum

REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"} #this is capitalized because thats the idiomatic way to do consts in python guy guys  guys -QV

class State(Enum):
  IDLE = 0
  READ = 1
  DOWNLOAD = 2
  VERIFY = 3
  EXTRACT = 4
  BUILD = 5
status = State.IDLE  # valera what is this for ??? # idk balera loves bibecoding but i made it slightly better with an enum i  guess -QV

# exceptions
class InvalidRecipeError(Exception):
  pass

class InvalidChecksumError(Exception):
  pass


# ANSI colors and printing
class Colors:
  ERROR = "\x1b[5;97;101m"
  WARNING = "\x1b[5;30;103m"
  SUCCESS = "\x1b[0;97;48;5;28m"
  SH_COMMAND = "\x1b[0;97;48;5;21m"
  END = "\033[0m"

def log(color: Colors, *args):
  print(f"{color if color is not None else ''}I:", *args, Colors.END)


class BuildContext: # https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
  ARCH = "x86_64" # RUDE: fuck arm developer
  CFLAGS = "" #"-Dick"
  CXXFLAGS = ""
  LDFLAGS = "" #"-Dick2"
  SRCDIR =  None # this is package source directory
  PKGDIR = None # this is package staging directory i.e. where it will be installed
  NPROC = 1
  LIBC = ""

  def __init__(self, builddir, portdir, recipe):
    self.BUILDDIR = builddir
    self.PORTDIR = portdir
    self.SRCDIR = os.path.join(builddir, "pkgsrc")
    self.PKGDIR = os.path.join(builddir, "pkgdir")
    os.makedirs(self.SRCDIR, exist_ok=True)
    os.makedirs(self.PKGDIR, exist_ok=True)    
    
    self.NPROC = os.cpu_count() if os.cpu_count() is not None else 1
    self.LIBC = "glibc" # switch to musl to break everything TODO: package musl
    # i think this is wrong? ARCH would refer to our target architecture whereas recipe arch is the arch it can be built for
    # TODO: this should be replaced with if checks
    self.ARCH = recipe["arch"]
    self.recipe = recipe
    self.recipe["depends"] = [self.LIBC if pkg == "libc" else pkg for pkg in self.recipe["depends"]]

    self.env = os.environ.copy()
    #self.env["DESTDIR"] = self.pkgdir
    #self.env["CFLAGS"] = self.CFLAGS
    pass

  def sh(self, *args):
    cwd = self.SRCDIR
    log(Colors.SH_COMMAND, f"+$ {' '.join(args)}")
    subprocess.run(args, cwd=cwd, env=self.env, check=True)

  def cp(self, frm, to):
    self.sh("cp", "-r", "-v", frm, to)

  def build(self):
    self.recipe["build"](self)

  def install(self):
    self.recipe["install"](self)


def read_recipe(path):
  with open(path, "r") as f:
    recipe_def = {}
    exec(f.read(), recipe_def)
    # TODO: probably should move verifying to a seperate function   
    # does this still need to be moved? i feel like its short enough now -QV
    recipe_keys = recipe_def.keys()
    missing_keys = REQUIRED_KEYS - recipe_keys #this is set subtraction 
    if missing_keys:
      raise InvalidRecipeError(f"This recipe is missing the {", ".join(missing_keys)} key(s)!")
    return recipe_def

def download_files(ctx, recipe, redownload):
  skip_extracting = False
  for url in recipe["sources"]:
    if url.startswith("https://") and not url.endswith(".git"):
      filename = url.split("/")[-1]
      dest = f"{ctx.BUILDDIR}/{filename}"
      if not os.path.exists(dest) or redownload:
        log(None, f"Downloading {url} to {dest}")
        urllib.request.urlretrieve(url, dest)
      else:
        log(None, f"{dest} already exists, skipping download!")
    
    elif url.startswith("git://"): # TODO: add cloning from https git
      skip_extracting = True
      dest = f"{ctx.SRCDIR}/{recipe["pkgname"]}"
      if not os.path.exists(dest) or redownload:
        log(None, f"Cloning {url} to {dest} via git")
        ctx.sh(f"git", "clone", "--depth", "1", url, dest)
      else: 
        log(None, f"{dest} already exists, skipping download!")
      
  return skip_extracting


def calc_checksum(path, algorithm="sha256"):
  hasher = hashlib.new(algorithm)
  with open(path, "rb") as file:
    while chunk := file.read(8192):
      hasher.update(chunk)
  return hasher.hexdigest()

def check_downloaded(ctx, shasum):
  successes = []
  files = []
  fails = []
  i = 0
  for url in recipe["sources"]:
      filename = url.split("/")[-1]
      dest = f"{ctx.BUILDDIR}/{filename}"
      files.append(dest)
      successes.append(calc_checksum(dest) == shasum[i])
  if not(False in successes):
    return True
  else:
    for i in range(len(files)):
      if not(successes[i]):
        fails.append(files[i])
    return fails


def extract_src(ctx, recipe):
  for url in recipe["sources"]:
    filename = url.split("/")[-1]
    dest = f"{ctx.BUILDDIR}/{filename}"
    with tarfile.open(dest, "r") as f:
      f.extractall(ctx.SRCDIR)


if __name__ == "__main__":
  ignoreintegrity = False
  parser = argparse.ArgumentParser(
                    prog='pbuild',
                    #suggest_on_error=True, # this doesn't work on my python 3.13
                    description='Compiles apk files to be used in Poppycrow Linux repos.',
                    epilog='See more @ github.com/Poppycrow-Linux/poppyports/')
  parser.add_argument('pkgpath', help='Path of the folder that contains the build recipe.')
  parser.add_argument('-ignoreintegrity', '-ii', '-ignore-broken-files', action='store_true', help='Ignore any checksum errors and continue building the package.')
  parser.add_argument('-fresh', '-new', '-redownload', action='store_true', help='Redownload files even if they are already present and pass the integrity checks.')
  parser.add_argument('builddir', help='The directory to build the recipe in.')
  args = parser.parse_args()
  pkgpath = args.pkgpath
  ignoreintegrity = args.ignoreintegrity
  builddir = args.builddir
  redownload = args.fresh

  #pkgpath = sys.argv[1]
  #builddir = sys.argv[2]

  status = State.READ
  log(None, "READING RECIPE")
  log(None, f"Arguments used: {args}")
  recipe = read_recipe(f"{pkgpath}/recipe.py")

  ctx = BuildContext(os.path.abspath(builddir), os.path.abspath(pkgpath), recipe)
  os.makedirs(ctx.BUILDDIR, exist_ok=True)

  status = State.DOWNLOAD
  log(None, "Downloading files")
  skip_extracting = download_files(ctx, recipe, redownload)

  if "sha256sum" in recipe:
    status = State.VERIFY
    log(None, "Checksum found in recipe, checking...")
    
    if check_downloaded(ctx, recipe["sha256sum"]) == True:
      log(Colors.SUCCESS, f"☑ Integrity check passed.")
    else:
      log(Colors.ERROR, f"!!!!!!!!!!!! INTEGRITY CHECK FAILED !!!!!!!!!!!!")
      log(Colors.ERROR, check_downloaded(ctx, recipe["sha256sum"]), " FAILED THE CHECKSUM")
      if not(ignoreintegrity):
        raise InvalidChecksumError("One or more file(s) did not pass the integrity check. Use -ii or -ignoreintegrity to bypass this error.")
  else:
    log(Colors.WARNING, f"//// SHA256 checksum not found in recipe {recipe["pkgname"]}, extracting without checks. ////")

  if not skip_extracting:
    status = State.EXTRACT
    log(None, "Extracting source...")
    extract_src(ctx, recipe)

  status = State.BUILD
  log(None, "Building...")
  ctx.build()
  ctx.install()


  # make apk
  def run_apk(*args):
    #env = os.environ.copy()
    #env["LD_LIBRARY_PATH"] = "staging/apk-install/lib/x86_64-linux-gnu/"
    subprocess.run(["apk"] + list(args), env=os.environ, check=True)

  outpath = f"{builddir}/{recipe['pkgname']}-{recipe['pkgver']}.apk"
  # the minimum you need to pass it seems?
  run_apk("mkpkg",
          "-I", f"name:{recipe["pkgname"]}",
          "-I", f"version:{recipe["pkgver"]}",
          "-F", ctx.PKGDIR,
          "-o", outpath)

  log(Colors.SUCCESS, f"Done! Generated {outpath}")



""" # this is old code
# create data media
def data_tar():
  buf = io.BytesIO()
  with tarfile.open(fileobj=buf, mode="w:gz") as f:
    for path, dirs, items in os.walk("build/pkgdir"):
      for item in items:
        f.add(f"{path}/{item}", arcname=item, recursive=False)
  return buf.getvalue()


#with tarfile.open("data.tar.gz.tmp", "w:gz") as f:
#  for path, items, _ in os.walk("build/pkgdir"):
#    for item in items:
#      f.add(f"{path}/{item}", arcname=item)

# write .PKGINFO i.e. control media
# https://wiki.alpinelinux.org/wiki/Apk_spec#PKGINFO_Format
def control_tar(pkginfo):
  buf = io.BytesIO()
  with tarfile.open(fileobj=buf, mode="w:gz") as f:
    info = tarfile.TarInfo(".PKGINFO")
    data = pkginfo.encode()
    info.size = len(data)
    info.mode = 0o644
    f.addfile(info, io.BytesIO(data))
  return buf.getvalue()
"""

"""
# TODO: figure out how to integrate this with the -I syntax of mkpkg
#       because it feels like they use different vars syntax
info_media = f\"""
pkgname = {recipe_def["pkgname"]}
pkgver = {recipe_def["pkgver"]}
pkgdesc = {recipe_def["pkgdesc"]}
url = {recipe_def["url"]}
arch = {recipe_def["arch"]}
license = {recipe_def["license"]}
\"""
"""
