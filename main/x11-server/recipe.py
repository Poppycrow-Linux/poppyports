recipever = 0
pkgname = "x11"
pkgver = "21.1.24"
pkgrel = 0
pkgdesc = "Demonspawn"
url = "https://x.org/"
arch = "x86_64"
license = ""


sources = [f"https://xorg.freedesktop.org/archive/individual/xserver/xorg-server-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/xorg-server-{pkgver}" # TODO fix this is because tar files have a top level name
  # https://stackoverflow.com/questions/70191105/got-an-error-while-building-wayland-error-program-dot-not-found
  c.sh("mkdir -p build")
  c.SRCDIR = c.SRCDIR + "/build"
  c.sh(f"../configure")
  c.sh("make",f"-j{c.NPROC}")


def install(c):
  c.sh("make","install",f"DESTDIR={c.PKGDIR}")
