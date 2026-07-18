pkgname = "lua"
pkgver = "5.4.8"
pkgrel = 0
pkgdesc = "lua"
url = "https://www.lua.org/"
arch = "x86_64"
license = "MIT"

sources = [f"https://www.lua.org/ftp/{pkgname}-{pkgver}.tar.gz"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + "/lua-5.4.8" # TODO fix this is because tar files have a top level name
  c.sh("make", "linux", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"INSTALL_TOP={c.PKGDIR}/usr")
