recipever = 0
pkgname = "parted"
pkgver = "3.7"
pkgrel = 0
pkgdesc = "gnu is a parted"
url = "https://www.gnu.org/software/parted/"
arch = "x86_64"
license = "MIT"

#sbu = None

sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.xz"]
depends = ['glibc','util-linux','libreadline','libuuid']


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(f"./configure --prefix={c.PKGDIR} --disable-device-mapper --disable-static --disable-pc98")
  c.sh(f"make -j{c.NPROC}")

def install(c):
  c.sh("make install")
