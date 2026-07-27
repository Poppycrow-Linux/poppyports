pkgname = "python3"
pkgver = "3.14.6"
pkgrel = 0
pkgdesc = f"Python 3 version {pkgver}"
url = "https://www.python.org/"
arch = "all"
license = "PSF-2.0"

sources = [f"https://www.python.org/ftp/python/{pkgver}/Python-{pkgver}.tar.xz"]
depends = ["libc"]


def build(c):
  c.SRCDIR += f"/Python-{pkgver}"
  c.sh("./configure", "--prefix=/usr")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
