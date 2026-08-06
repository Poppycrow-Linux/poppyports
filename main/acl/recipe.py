recipever = 0
pkgname = "acl"
pkgver = "2.4.0"
pkgrel = 0
pkgdesc = "access control list utilities and library"
url = "https://savannah.nongnu.org/projects/acl"
arch = "x86_64"
license = "LGPL-2.1-or-later AND GPL-2.0-or-later"


sources = [f"https://download.savannah.nongnu.org/releases/acl/{pkgname}-{pkgver}.tar.xz"]
depends = []
makedepends = ["attr"]


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(
    "./configure",
    "--prefix=/usr",
    "--disable-static",
    f"--docdir=/usr/share/doc/{pkgname}-{pkgver}", #we don't really need a docdir but whatever'
    f"CFLAGS={c.CFLAGS}",
    f"LDFLAGS={c.LDFLAGS}",
  )
  c.sh("make", f"-j{c.NPROC}")


def install(c):
  c.sh("make", f"DESTDIR={c.PKGDIR}", "install")
