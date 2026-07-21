recipever = 0
pkgname = "wayland"
pkgver = "1.26.0"
pkgrel = 0
pkgdesc = "wayland"
url = "https://wayland.freedesktop.org/"
arch = "x86_64"
license = "MIT"

sources = [f"https://gitlab.freedesktop.org/wayland/wayland/-/archive/1.26.0/wayland-1.26.0.tar.gz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + "/wayland-1.26.0" # TODO fix this is because tar files have a top level name
  c.sh("meson","build/",f"--prefix={c.PKGDIR}")

def install(c):
  c.sh("ninja", "-C", "build/", "install")
