recipever = 0
pkgname = "libxo"
pkgver = "2.0.0"
pkgrel = 0
pkgdesc = "A Library for Generating Text, XML, JSON, and HTML Output." #It's in core because it's needed both for bsdutils and chimerautils
url = "https://github.com/Juniper/libxo"
arch = "x86_64"
license = "BSD-2-Clause"


sources = [f"{url}/releases/download/{pkgver}/{pkgname}-{pkgver}.tar.gz"]
depends = []
makedepends = ['byacc', 'make']

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(f'patch -p1 -i "{c.PORTDIR}/patches/lintl.patch"')
  if "CFLAGS" in c.env:
      c.env["CFLAGS"] += " -std=c17"
  else:
      c.env["CFLAGS"] = "-std=c17"
  c.sh(f"sh {c.SRCDIR}/bin/setup.sh", shell = True)
  c.sh(f"sh {c.SRCDIR}/configure --prefix=/usr", cwd=f"{c.SRCDIR}/build", shell = True)
  c.sh("make", cwd = f"{c.SRCDIR}/build", shell = True)


def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}", cwd = f"{c.SRCDIR}/build", shell = True) # bash adds its own /usr for some reason
