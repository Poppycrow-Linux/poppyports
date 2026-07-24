recipever = 0
pkgname = "dwm"
pkgver = "6.8"
pkgrel = 0
pkgdesc = "dwm is a dynamic window manager for X."
url = "https://dwm.suckless.org/"
arch = "x86_64"
license = "MIT/X Consortium License"

sbu = 0.9

#https://dl.suckless.org/dwm/dwm-6.8.tar.gz
sources = [f"https://dl.suckless.org/{pkgname}/{pkgname}-{pkgver}.tar.gz"]
depends = ["x11-server"]


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("make", f"{c.SRCDIR}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
