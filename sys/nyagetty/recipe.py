recipever = 0
pkgname = "nyagetty"
pkgver = "2.38.99"
pkgrel = 0
pkgdesc = "Standlone agetty"
url = "https://github.com/chimera-linux/nyagetty"
arch = "x86_64"
license = "0BSD"

sources = [f"https://github.com/chimera-linux/nyagetty/archive/refs/tags/v2.38.99.tar.gz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("meson","build/",f"--prefix={c.PKGDIR}")
  c.sh("meson","compile","-C","build",)

# this package has too many prices and values
def install(c):
  c.sh("mkdir","-p",f"{c.PKGDIR}/bin")
  c.cp(f"{c.SRCDIR}/build/agetty",f"{c.PKGDIR}/bin/agetty")
