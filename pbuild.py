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

# exceptions
class InvalidRecipeError(Exception):
  pass

class BuildContext: # https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
  ARCH = "x86_64" # RUDE: fuck arm developer
  CFLAGS = "" #"-Dick"
  CXXFLAGS = ""
  LDFLAGS = "" #"-Dick2"
  SRCDIR =  None # this is package source directory
  PKGDIR = os.getcwd() # this is package staging directory i.e. where it will be installed
  
  def __init__(self, srcdir, pkgdir, recipe):
    self.SRCDIR = srcdir
    self.PKGDIR = pkgdir
    self.env = os.environ.copy()
    self.ARCH = recipe["arch"]
    self.recipe = recipe
    #self.env["DESTDIR"] = self.pkgdir
    #self.env["CFLAGS"] = self.CFLAGS
    pass
  
  def sh(self, *args):
    cwd = self.SRCDIR
    print(f"+$ {' '.join(args)}")
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
    for key in ["sources", "pkgname", "build", "install", "arch"]:
      if not key in recipe_def.keys():
        invalid_keys.append(key)
    if len(invalid_keys) >= 1:
      raise InvalidRecipeError(f"This recipe is missing the {", ".join(invalid_keys)} key(s)!")
    return recipe_def

def download_files(ctx, recipe):
  for url in recipe["sources"]:
    filename = url.split("/")[-1]
    dest = f"build/{filename}"
    print(f"!! Down Loading {url} to {dest}")
    if not os.path.exists(dest):
      urllib.request.urlretrieve(url, dest)
    
    print(f"!! tar xtracting")
    with tarfile.open(dest, "r") as f:
      os.makedirs(ctx.SRCDIR, exist_ok=True)
      f.extractall(ctx.SRCDIR)


if __name__ == "__main__":
  pkgpath = sys.argv[1]

  print("!! READING RECIPE")
  recipe = read_recipe(f"{pkgpath}/recipe.py")

  ctx = BuildContext(f"{os.getcwd()}/build/pkgsrc", f"{os.getcwd()}/build/pkgdir", recipe)
  os.makedirs("build", exist_ok=True)
  
  print("!! Download files")
  download_files(ctx, recipe)

  print("!! Ok running build")
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

  print("!! done!!!!")



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
