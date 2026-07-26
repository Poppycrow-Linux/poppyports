recipever = 0
pkgname = "go"
pkgver = "1.26.5"
pkgrel = 0
pkgdesc = "lua"
url = "https://www.lua.org/"
arch = "x86_64"
license = "BSD-3-Clause"


sources = [f"https://go.dev/dl/{pkgname}{pkgver}.src.tar.gz"]
sha256sum = ["495be4bc87176ac567392e5b4116abd98466d33d7b49d41e764ccc6976b2dc42"]
depends = []
makedepends = ['git']


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}/src" # TODO fix this is because tar files have a top level name. except this time it just works?
  c.sh(f"GOROOT={c.PKGDIR}/usr/sbin ./make.bash")

def install(c):
  pass
