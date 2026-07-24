recipever = 0
pkgname = "weston"
pkgver = "16.0.0"
pkgrel = 0
pkgdesc = "A Wayland Compositor"
url = "https://wayland.freedesktop.org/"
arch = "x86_64"
license = "MIT"

sources = [f"https://gitlab.freedesktop.org/wayland/weston/-/archive/16.0.0/weston-16.0.0.tar.gz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + "/weston-16.0.0" # TODO fix this is because tar files have a top level name
  c.sh("meson","build/",f"--prefix={c.PKGDIR}")

# this package has too many prices and values
def install(c):
  c.sh("ninja", "-C", f"-j{c.NPROC}", "build/", "install")
