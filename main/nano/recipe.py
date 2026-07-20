pkgname = "nano"
pkgver = "9.1"
pkgrel = 0
pkgdesc = "The GNU Nano Text Editor"
url = "https://www.nano-editor.org/"
arch = "x86_64"
license = "GPLv3"


sources = [f"https://www.nano-editor.org/dist/v9/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ["2647a33f3c2ff3dc45168aeccff61abc7eae8bf99ac1d35574175c23bde6050b"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("./configure")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
