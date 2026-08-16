recipever = 0
pkgname = "bsdutils"
pkgver = "14.3"
pkgrel = 0
pkgdesc = "Alternative to GNU coreutils using software from FreeBSD"
url = "https://codeberg.org/dcantrell/bsdutils"
arch = "x86_64"
license = "BSD-3-Clause"


sources = [f"https://codeberg.org/dcantrell/bsdutils/archive/{pkgver}-RELEASE.tar.gz"]
sha256sum = ["26f528e1cd4ce66e2d8108620df1883ff577d5e4591b884336e51ac56af18717"]
depends = ["libc", "libxo", "libedit", "ncurses", "openssl"]
makedepends = ['byacc', 'meson']


def build(c):
  c.SRCDIR = c.SRCDIR + f"/bsdutils"
  c.sh("meson", "setup", "build/")
  c.sh("ninja","-C","build/")

def install(c):
  c.sh("bash", "-c", f"mkdir -p {c.PKGDIR}/bin; for i in $(ls build/src); do cp build/src/$i/$i {c.PKGDIR}/bin/; done;")
