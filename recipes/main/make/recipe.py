# what the fuck would the convention for make be because theres also say bsdmake should this be gmake?? thoughts?
pkgname = "make"
pkgver = "4.4.1"
pkgrel = 0
pkgdesc = "GNU Make Utility"
url = "https://www.gnu.org/savannah-checkouts/gnu/make/manual/make.html"
arch = "all"
license = "GPLv3"
maintainer = "samxyz30"

sources = [f"https://ftp.gnu.org/gnu/make/make-{pkgver}.tar.gz"]
sha256sum = ["dd16fb1d67bfab79a72f5e8390735c49e3e8e70b4945a15ab1f81ddb78658fb3"]
depends = ["libc"]


def build(c):
  c.SRCDIR += f"/make-{pkgver}"
  c.sh("./configure", "--prefix=/usr", "--without-guile")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
