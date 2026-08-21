recipever = 0
pkgname = "muon"
pkgver = "1.0"
pkgrel = 0
pkgdesc = "C99 implementation of the Meson build system compat symlink()"
url = "https://muon.build/"
arch = "x86_64"
license = "GPLv3"

sources = []
depends = ['muon']


def build(c):
    pass

def install(c):
  c.sh(f"mkdir -p {c.PKGDIR}/usr/bin")
  c.lnk(f"{c.PKGDIR}/usr/bin/muon", f"{c.PKGDIR}/usr/bin/meson", relative = True)
