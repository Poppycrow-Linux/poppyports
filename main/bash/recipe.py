pkgname = "bash"
pkgver = "5.3"
pkgrel = 0
pkgdesc = "Bash is the GNU Project's shell—the Bourne Again SHell. This is an sh-compatible shell that incorporates useful features from the Korn shell (ksh) and the C shell (csh)."
url = "https://www.gnu.org/software/bash/"
arch = "x86_64"
license = "GPL v3 or later"


sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ["0d5cd86965f869a26cf64f4b71be7b96f90a3ba8b3d74e27e8e9d9d5550f31ba"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(c.SRCDIR + "/configure")
  c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
