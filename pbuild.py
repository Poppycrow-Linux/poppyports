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
import time
import threading
import configparser
from enum import Enum

REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"} #this is capitalized because thats the idiomatic way to do consts in python guy guys  guys -QV


start_time = time.time()
total_time = 0 #ms
last_time = 0 
time_spent_on_state = 0 # ms
time_spent = {} # state to ms
stop_event = threading.Event()
supressnonerrorlogs = False #set as a global variable so the log function would Know
color = True # same as above

class State(Enum):
  IDLE = 0
  READ = 1
  DOWNLOAD = 2
  VERIFY = 3
  EXTRACT = 4
  BUILD = 5
  DONE = 6

status = State.IDLE
def change_status(target:State):
  global time_spent
  global last_time
  global status
  time_spent[status] = time_spent_on_state
  last_time = total_time
  

  status = target

def passive_timer():
    global time_spent_on_state
    global total_time
    while not stop_event.is_set():
        total_time = 1000*(time.time() - start_time)
        time_spent_on_state = total_time - last_time
        time.sleep(0.1)

timer_thread = threading.Thread(target=passive_timer, daemon=True)
timer_thread.start()
  
# exceptions
class InvalidRecipeError(Exception):
  pass

class InvalidChecksumError(Exception):
  pass

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
            raise argparse.ArgumentTypeError(
                f"invalid boolean value for {option_string}: {values}"
            )

# ANSI colors and printing
class Colors:
  ERROR = "\x1b[5;97;101m"
  WARNING = "\x1b[5;30;103m"
  SUCCESS = "\x1b[0;97;48;5;28m"
  SH_COMMAND = "\x1b[0;97;48;5;21m"
  END = "\x1b[0m"

def log(clr: Colors, *args):
    if (supressnonerrorlogs and (clr in {Colors.SUCCESS, Colors.ERROR, Colors.WARNING})) or not(supressnonerrorlogs):
      print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)


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
    self.LIBC = "glibc" # switch to musl to break everything TODON'T: package musl
    # i think this is wrong? ARCH would refer to our target architecture whereas recipe arch is the arch it can be built for
    # TODO: this should be replaced with if checks
    self.ARCH = recipe["arch"]
    self.recipe = recipe
    self.recipe["depends"] = [self.LIBC if pkg == "libc" else pkg for pkg in self.recipe["depends"]]

    self.env = os.environ.copy()
    #self.env["DESTDIR"] = self.pkgdir
    #self.env["CFLAGS"] = self.CFLAGS
    pass

  def sh(self, *args, cwd=None, shell=False):
    if cwd is None:    cwd = self.SRCDIR
    if len(args) == 1: shell = True

    # shell=True requires a string to be passed in i assume
    cmd = ' '.join(args) if shell else args

    log(Colors.SH_COMMAND, f"+$ {' '.join(args) if isinstance(cmd, tuple) else cmd}")
    subprocess.run(cmd, cwd=cwd, env=self.env, check=True, shell=shell)



  def cp(self, frm, to):
    self.sh("cp", "-r", "-v", frm, to)

  def lnk(self, frm, to):
    self.sh("ln", "-s", frm, to)

  def apply_patches(self):
    patchdir = self.PORTDIR + "/patches"
    if not os.path.exists(patchdir): return # no patches to apply
    for path, dirs, files in os.walk(patchdir):
      for patch in files:
        self.sh("patch", "-p1", "-i", f"{path}/{patch}")


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


def build_state_breakdown():
  def truncate(num, places):
      if places == 0:
          return str(int(num))
      s = str(num)
      if 'e' in s or 'E' in s:
          s = f"{num:.15f}"
      before_dec, after_dec = s.split('.')
      return f"{before_dec}.{after_dec[:places]}"

  global time_spent
  result = ""
  for s,t in time_spent.items():
    measurement = "ms"
    divisor = 1
    if t > 60000:
      measurement = "min"
      divisor = 60000
    elif t > 1000: #seconds
      measurement = "s"
      divisor = 1000
    result += f"{s.name}: {truncate(t/divisor, 5)} ({measurement})\n"
  return result


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
  parser = argparse.ArgumentParser(
                    prog='pbuild',
                    #suggest_on_error=True, # this doesn't work on my python 3.13
                    description='Compiles apk files to be used in Poppycrow Linux repos.',
                    epilog='See more @ github.com/Poppycrow-Linux/poppyports/')
  parser.add_argument('pkgpath', help='Path of the folder that contains the build recipe.')
  parser.add_argument('-ignoreintegrity', '-ii', '-ignore-broken-files', action = OptionalBoolAction, help='Ignore any checksum errors and continue building the package.', nargs = "?")
  parser.add_argument('-fresh', '-new', '-redownload', action = OptionalBoolAction, help='Redownload files even if they are already present and pass the integrity checks.', nargs = "?")
  parser.add_argument('-rebuild', action = OptionalBoolAction, help='Force rebuild even when package is already built.', nargs = "?")
  parser.add_argument('-color', action = OptionalBoolAction, help='Highlight warnings, errors and build completion.', nargs = "?")
  parser.add_argument('-buildstatebreakdown', '-bsbd', '-bb', action = OptionalBoolAction, help='Show build state breakdown.', nargs = "?")
  parser.add_argument('-supressnonerrorlogs', '-clean-logs', action = OptionalBoolAction, help="Supress logs that aren't warnings, errors, or completion messages", nargs = "?")
  parser.add_argument('builddir', help='The directory to build the recipe in.', nargs = "?")
  parser.add_argument('-config', help='The config to use.', nargs = "?")
  args = parser.parse_args()


  CONFIGFILEPATH = "./pbuild.conf"
  if args.config: # parse configfilepath earlier than the rest so we can override it
    CONFIGFILEPATH = args.config


  # fallback variables

  ignoreintegrity = False
  color = True
  rebuild = False
  show_bs_breakdown = True
  supressnonerrorlogs = False

  #TODO: move config reading to a separate function

  configparser = configparser.ConfigParser()
  configparser.read(CONFIGFILEPATH)
  if configparser.sections() == []:
        configparser['Build'] = {"AssumeRebuild" : "no",
                      "AssumeRedownload" : "no",
                      "DefaultBuildPath" : "./build",
                      "AssumeRebuild" : "no",
                      "AssumeIgnoreIntegrity" : "no"
                        }
        configparser['Display'] = {"Color" : "yes",
                        "SupressNonErrorLogs" : "no",
                        "BuildStateBreakdown" : "yes"
                        }
        configfile = open(CONFIGFILEPATH, 'w')

  if os.path.getsize(CONFIGFILEPATH) == 0: ## create and write default config if it is missing
    configparser.write(configfile) ## TODO: write default config sections if missing. maybe not needed (question Mark), since the defaults are kind of above

  ignoreintegrity = configparser.getboolean('Build', 'AssumeIgnoreIntegrity')
  redownload = configparser.getboolean('Build', 'AssumeRedownload')
  builddir = configparser['Build']['DefaultBuildPath']
  color = configparser.getboolean('Display', 'Color')
  supressnonerrorlogs = configparser.getboolean('Display', 'SupressNonErrorLogs')
  rebuild = configparser.getboolean('Build', 'AssumeRebuild')
  show_bs_breakdown = configparser.getboolean('Display', 'BuildStateBreakdown')



  if (args.pkgpath != None): pkgpath = args.pkgpath # ifs added so that cmdline functions cannot override shit when they are not set
  if (args.ignoreintegrity != None): ignoreintegrity = args.ignoreintegrity
  if (args.builddir != None): builddir = args.builddir
  if (args.color != None): color = args.color
  if (args.fresh != None): redownload = args.fresh
  if (args.supressnonerrorlogs != None): supressnonerrorlogs = args.supressnonerrorlogs
  if (args.rebuild != None): rebuild = args.rebuild
  if (args.buildstatebreakdown != None): show_bs_breakdown = args.buildstatebreakdown


  #pkgpath = sys.argv[1]
  #builddir = sys.argv[2]

  change_status(State.READ)
  log(None, "READING RECIPE")
  log(None, f"Arguments used: {args}")
  recipe = read_recipe(f"{pkgpath}/recipe.py")

  ctx = BuildContext(os.path.abspath(builddir), os.path.abspath(pkgpath), recipe)
  os.makedirs(ctx.BUILDDIR, exist_ok=True)


  outpath = f"{builddir}/{recipe['pkgname']}-{recipe['pkgver']}.apk"
  if os.path.exists(outpath) and not rebuild:
    log(Colors.WARNING, f"Skipping build as {outpath} already exists. If you need to rebuild, pass the -rebuild flag to force rebuilding.")
    sys.exit(0)

  change_status(State.DOWNLOAD)
  log(None, "Downloading files")
  skip_extracting = download_files(ctx, recipe, redownload)

  if "sha256sum" in recipe:
    change_status(State.VERIFY)
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
    change_status(State.EXTRACT)
    log(None, "Extracting source...")
    extract_src(ctx, recipe)

  change_status(State.BUILD)
  log(None, "Building...")
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
          "-o", outpath)
  change_status(State.DONE)

  log(Colors.SUCCESS, f"Done! Generated {outpath}")
  stop_event.set()
  if show_bs_breakdown:
    print()
    log(Colors.SUCCESS, f"Build State Breakdown: (With {NPROC} passed to NPROC)")
    print()
    print(build_state_breakdown())



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
