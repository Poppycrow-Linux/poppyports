pkgname = "readline"
pkgver = "8.2.13"
pkgrel = 0
pkgdesc = "GNU Readline Utility"
url = "https://tiswww.case.edu/php/chet/readline/rltop.html"
arch = "x86_64"
license = "GPLv3 or later"


sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.gz"]
depends = ["libc", 'ncurses']


def build(c):
  c.SRCDIR += f"/{pkgname}-{pkgver}"
  c.sh("./configure", "--prefix=/usr")

  if c.ARCH == "x86_64": #x86 needs PIC (smartPICed.com)
      if "CFLAGS" in c.env:
        c.env["CFLAGS"] += " -fPIC"
      else:
        c.env["CFLAGS"] = "-fPIC"

  c.sh("make", f"-j{c.NPROC}", "SHLIB_LIBS=-lncurses")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
