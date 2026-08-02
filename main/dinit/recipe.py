recipever = 0
pkgname = "dinit"
pkgver = "0.22.1"
pkgrel = 0
pkgdesc = "Service manager and the init system."
url = "https://github.com/davmac314/dinit"
arch = "x86_64"
license = "Apache v2"

sbu = 0.5

# https://github.com/davmac314/dinit/archive/refs/tags/v0.22.1.tar.gz
sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
depends = ["libstdc++"]
makedepends = ["make"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  configureflags = [
    "--disable-strip",
    "--enable-shutdown",
    "--platform=Linux",
    "--sbindir=/usr/sbin",
    "--syscontrolsocket=/run/dinitctl"
  ]


  c.sh("make mconfig") #TODO: edit mconfig
  c.sh("./configure", *configureflags)
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
