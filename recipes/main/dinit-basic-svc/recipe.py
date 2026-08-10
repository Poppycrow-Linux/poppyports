recipever = 0
pkgname = "dinit-basic-svc"
pkgver = "0.22.1"
pkgrel = 0
pkgdesc = "Service manager and the init system. (Example service files)"
url = "https://github.com/davmac314/dinit"
arch = "x86_64"
license = "Apache v2"

sbu = 0.5

# https://github.com/davmac314/dinit/archive/refs/tags/v0.22.1.tar.gz
sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
depends = ["libstdc++"]
makedepends = ["make"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/dinit-{pkgver}"
def install(c):
  c.sh(f"mkdir -p {c.PKGDIR}/usr/lib/dinit.d")
  c.sh("cp", "-r" ,f"{c.SRCDIR}/doc/linux/services/*", f"{c.PKGDIR}/usr/lib/dinit.d", shell = True)
