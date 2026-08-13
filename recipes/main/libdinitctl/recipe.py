recipever = 0
pkgname = "libdinitctl"
pkgver = "0_git20250424"
_gitrev = "4ed774d5b427eeb30a97167decbe0009733355bc"
pkgrel = 0
pkgdesc = "High level API for dinitctl socket interface"
url = "https://github.com/chimera-linux/libdinitctl"
arch = "x86_64"
license = "BSD-2-Clause"

sources = [f"https://github.com/chimera-linux/libdinitctl/archive/{_gitrev}.tar.gz"]
sha256sum = ["3805bbf236c7b2421f8921a1643bcbfcecfd4edd68d9737282759f85842b8950"]
depends = []
makedepends = ["meson", "ninja", "pkgconf"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{_gitrev}"
  c.sh("meson","setup",f"--prefix={c.PKGDIR}/usr", f"build/")
  c.sh("ninja", "-C", f"build/")

def install(c):
  c.sh("ninja", "-C", f"build/", "install")
