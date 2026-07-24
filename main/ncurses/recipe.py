recipever = 0
pkgname = "ncurses"
pkgver = "6.6"
pkgrel = 0
pkgdesc = "Free software emulation of curses in System V Release 4.0 (SVr4), and more."
url = "https://invisible-island.net/ncurses/"
arch = "x86_64"
license = "MIT/X11"
maintainer = "cachewave"

sbu = 1.0

sources = [f"https://ftp.gnu.org/gnu/ncurses/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ["355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("./configure","--enable-widec","--with-shared","--without-normal","--without-debug","--with-termlib")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}", f"-j{c.NPROC}") # should be also symlinked to /lib64
  c.SRCDIR = c.PKGDIR + "/usr/lib" # hack because sh doesnt allow to set cwd
  c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so.6")
  c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so")
  c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so.6.6")
