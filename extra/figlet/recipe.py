recipever = 0
pkgname = "figlet"
pkgver = "2.2.5"
pkgrel = 0
pkgdesc = "Figlet"
url = "https://github.com/cmatsuoka/figlet"
arch = "x86_64"
license = "BSD3"

sbu = 0.0


sources = [f"https://github.com/cmatsuoka/figlet/archive/refs/tags/{pkgver}.tar.gz"]
depends = ['glibc']


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("patch", "-p1", "-i", c.PORTDIR + "/ahhhh.patch")
  c.sh("make","figlet",f"PREFIX={c.PKGDIR}", f"DESTDIR={c.PKGDIR}")
  #c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"PREFIX={c.PKGDIR}", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
