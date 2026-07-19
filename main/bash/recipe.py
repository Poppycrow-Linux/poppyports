pkgname = "bash"
pkgver = "5.3"
pkgrel = 0
pkgdesc = "Bash is the GNU Project's shell—the Bourne Again SHell. This is an sh-compatible shell that incorporates useful features from the Korn shell (ksh) and the C shell (csh)."
url = "https://www.gnu.org/software/bash/"
arch = "x86_64"
license = "GPL v3 or later"


sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.gz"]
#sha256sum = ["4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(c.SRCDIR + "/configure")
  c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
