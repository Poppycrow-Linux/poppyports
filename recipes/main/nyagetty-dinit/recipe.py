
recipever = 0
pkgname = "nyagetty"
pkgver = "2.38.99"
pkgrel = 0
pkgdesc = "Dinit services for nyagetty"
url = "https://github.com/chimera-linux/nyagetty"
arch = "x86_64"
license = "BSD-2-Clause"

sources = []
depends = []

def build(c):
    pass


def install(c):
  c.sh("mkdir","-p",f"{c.PKGDIR}/usr/")
  c.sh("mkdir","-p",f"{c.PKGDIR}/usr/lib")
  c.sh("mkdir","-p",f"{c.PKGDIR}/usr/lib/dinit.d")
  c.cp(f"{c.PORTDIR}/svc/.", f"{c.PKGDIR}/usr/lib/dinit.d")
  c.cp(f"{c.PORTDIR}/sh/.", f"{c.PKGDIR}/usr/lib/")
  c.sh(f"chmod -R +x {c.PKGDIR}/usr/lib/")
