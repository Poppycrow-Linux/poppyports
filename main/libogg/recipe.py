recipever = 0
pkgname = "libogg"
pkgver = "1.3.6"
pkgrel = 0
pkgdesc = "Ogg bitstream file format library"
url = "https://xiph.org/ogg"
arch = "all"
license = "BSD-3-Clause"
maintainer = "samxyz30"

sources = [f"https://downloads.xiph.org/releases/ogg/libogg-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.SRCDIR += f"/libogg-{pkgver}"

  c.sh("./configure", "--prefix=/usr")
  c.sh("make", f"-j{c.NPROC}")


def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
