recipever = 0
pkgname = "libcap-ng"
pkgver = "0.9.3"
pkgrel = 0
pkgdesc = "The libcap-ng library should make programming with POSIX capabilities easier."
url = "https://github.com/stevegrubb/libcap-ng"
arch = "x86_64"
license = "GPL-2.0-only"

sbu = 0.1



sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
depends = []
makedepends = ["make", "linux-headers", "pkgconf"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("./autogen.sh")
  c.sh("./configure")
  c.sh("make")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
