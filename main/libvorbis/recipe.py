recipever = 0
pkgname = "libvorbis"
pkgver = "1.3.7"
pkgrel = 0
pkgdesc = "Vorbis general audio compression codec"
url = "https://xiph.org/vorbis"
arch = "all"
license = "BSD-3-Clause"
maintainer = "samxyz30"

sources = [f"https://downloads.xiph.org/releases/vorbis/libvorbis-{pkgver}.tar.xz"]
depends = ["libogg"]

def build(c):
  c.SRCDIR += f"/libvorbis-{pkgver}"

  c.sh("./configure", "--prefix=/usr")
  c.sh("make", f"-j{c.NPROC}")


def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
