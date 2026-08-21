recipever = 0
pkgname = "ninja"
pkgver = "1.13.2"
pkgrel = 0
pkgdesc = "The ninja build system"
url = "https://ninja-build.org/"
arch = "x86_64"
license = "Apache-2.0"

sources = [f"https://github.com/ninja-build/ninja/archive/refs/tags/v{pkgver}.tar.gz"]
depends = []
makedepends = ['python', 're2c'] # re2c is not really needed but it gave me a warning when i didn't have it'

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("./configure.py --bootstrap")
  c.sh("./ninja all",)

# this package has too many prices and values
def install(c):
  c.sh("mkdir","-p",f"{c.PKGDIR}/usr/bin")
  c.cp("./ninja", f"{c.PKGDIR}/usr/bin")

