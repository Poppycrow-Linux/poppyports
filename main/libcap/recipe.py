recipever = 0
pkgname = "libcap"
pkgver = "2.78"
pkgrel = 0
pkgdesc = "POSIX.1e capabilities suite"
url = "http://sites.google.com/site/fullycapable"
arch = "x86_64"
license = "GPL-2.0-only"

sbu = 0.1


sources = [f"https://www.kernel.org/pub/linux/libs/security/linux-privs/libcap2/{pkgname}-{pkgver}.tar.xz"]
depends = []
makedepends = ["make", "attr-devel", "linux-headers", "pkgconf", "perl"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("make")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
