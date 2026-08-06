recipever = 0
pkgname = "attr"
pkgver = "2.6.0"
pkgrel = 0
pkgdesc = "utilities for managing filesystem extended attributes"
url = "https://savannah.nongnu.org/projects/attr"
arch = "x86_64"
license = "LGPL-2.1-or-later"


sources = [f"https://download.savannah.nongnu.org/releases/attr/{pkgname}-{pkgver}.tar.xz"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(
    "./configure",
    "--prefix=/usr",
    "--sysconfdir=/etc",
    "--disable-static",
    "--disable-silent-rules",
    f"CFLAGS={c.CFLAGS}",
    f"LDFLAGS={c.LDFLAGS}",
  )
  c.sh("make", f"-j{c.NPROC}")


def install(c):
  c.sh("make", f"DESTDIR={c.PKGDIR}", "install")
