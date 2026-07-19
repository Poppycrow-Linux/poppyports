# hi this is staging build system prototyping bullshit rn this is how you do apk
# i need to clean up - sam
# TODO: handle depends and also like basically redo what chimera and APKBUILDs do
# TODO: Everything.
import os
import sys
import io
import subprocess
import urllib.request
import tarfile
import hashlib
status = "idle"

# exceptions
class InvalidRecipeError(Exception):
  pass

class InvalidChecksum(Exception):
  pass


class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    ERROR = "\x1b[5;97;101m"
    WARNING = "\x1b[5;30;103m"
    SUCCESS = "\x1b[0;97;48;5;28m"
    SHCOMMAND = "\x1b[0;97;48;5;21m"
    END = "\033[0m"
    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            kernel32 = __import__("ctypes").windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32


class BuildContext: # https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
  ARCH = "x86_64" # RUDE: fuck arm developer
  CFLAGS = "" #"-Dick"
  CXXFLAGS = ""
  LDFLAGS = "" #"-Dick2"
  SRCDIR =  None # this is package source directory
  PKGDIR = os.getcwd() # this is package staging directory i.e. where it will be installed
  NPROC = 1

  def __init__(self, srcdir, pkgdir, recipe):
    self.SRCDIR = srcdir
    self.PKGDIR = pkgdir
    self.NPROC = os.cpu_count() if os.cpu_count() is not None else 1
    self.env = os.environ.copy()
    self.ARCH = recipe["arch"]
    self.recipe = recipe
    #self.env["DESTDIR"] = self.pkgdir
    #self.env["CFLAGS"] = self.CFLAGS
    pass

  def sh(self, *args):
    cwd = self.SRCDIR
    print(f"{Colors.SHCOMMAND}+$ {' '.join(args)}{Colors.END}")
    subprocess.run(args, cwd=cwd, env=self.env, check=True)

  def build(self):
    self.recipe["build"](self)

  def install(self):
    self.recipe["install"](self)

  def cp(self, input, output):
    raise RuntimeError("unimplemented")


def read_recipe(path):
  with open(path, "r") as f:
    recipe_def = {}
    exec(f.read(), recipe_def)
    # TODO: probably should move verifying to a seperate function
    invalid_keys = []
    for key in ["sources", "pkgname", "build", "install", "arch", "pkgver"]:
      if not key in recipe_def.keys():
        invalid_keys.append(key)
    if len(invalid_keys) >= 1:
      raise InvalidRecipeError(f"This recipe is missing the {", ".join(invalid_keys)} key(s)!")
    return recipe_def

def download_files(ctx, recipe):
  skip_extracting = False
  for url in recipe["sources"]:
    if url.startswith("https://") and not url.endswith(".git"):
      filename = url.split("/")[-1]
      dest = f"build/{filename}"
      if not os.path.exists(dest):
        urllib.request.urlretrieve(url, dest)
        print(f"I: Downloading {url} to {dest}")
      else: print("I:",dest, "already exists, skipping download!")
    elif url.startswith("git://"): # TODO: add cloning from https git
      skip_extracting = True
      dest = f"{ctx.SRCDIR}/{recipe["pkgname"]}"
      if not os.path.exists(dest):
        print(f"I: Cloning {url} to {dest}")
        #ctx.sh(f"git","clone","--depth 1",url,dest)
        subprocess.run(("git","clone","--depth","1",url,dest),cwd=os.getcwd())
      else: print("I:",dest, "already exists, skipping download!")
  return skip_extracting


def calc_checksum(path, algorithm="sha256"):
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_downloaded(shasum):
  successes = []
  files = []
  fails = []
  i = 0
  for url in recipe["sources"]:
      filename = url.split("/")[-1]
      dest = f"build/{filename}"
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
      dest = f"build/{filename}"
      with tarfile.open(dest, "r") as f:
        os.makedirs(ctx.SRCDIR, exist_ok=True)
        f.extractall(ctx.SRCDIR)


if __name__ == "__main__":
  pkgpath = sys.argv[1]

  status = "read_recipe"
  print("I: READING RECIPE")
  recipe = read_recipe(f"{pkgpath}/recipe.py")

  ctx = BuildContext(f"{os.getcwd()}/build/pkgsrc", f"{os.getcwd()}/build/pkgdir", recipe)
  os.makedirs("build", exist_ok=True)

  status = "download"
  print("I: Downloading files")
  skip_extracting = download_files(ctx, recipe)

  if "sha256sum" in recipe:
    status = "verification"
    print("I: Checksum found in recipe, checking...")
    if check_downloaded(recipe["sha256sum"]) == True:
      print(f"{Colors.LIGHT_GREEN}I: ☑ Integrity check passed. {Colors.END}")
    else:
      print(f"{Colors.ERROR}!!!!!!!!!!!! INTEGRITY CHECK FAILED !!!!!!!!!!!!{Colors.END}") #TODO: tell what file failed.
      print(check_downloaded(recipe["sha256sum"]), sep =" FAILED THE CHECKSUM\n", end = " FAILED THE CHECKSUM\n")
  else:
    print(f"{Colors.WARNING}// SHA256 checksum not found in recipe {recipe["pkgname"]}, extracting without checks. {Colors.END}")

  if not skip_extracting:
    status = "extract"
    print("I: Xtracting the tar")
    extract_src(ctx, recipe)

  status = "build"
  print("I: Ok running build")
  ctx.build()
  ctx.install()


  # make apk
  def run_apk(*args):
    #env = os.environ.copy()
    #env["LD_LIBRARY_PATH"] = "staging/apk-install/lib/x86_64-linux-gnu/"
    subprocess.run(["apk"] + list(args), env=os.environ, check=True)

  # the minimum you need to pass it seems?
  run_apk("mkpkg",
          "-I", f"name:{recipe["pkgname"]}",
          "-I", f"version:{recipe["pkgver"]}",
          "-F", ctx.PKGDIR,
          "-o", f"{recipe['pkgname']}-{recipe['pkgver']}.apk")

  print(f"{Colors.SUCCESS}I: Done{Colors.END}")



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
