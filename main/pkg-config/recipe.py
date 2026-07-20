pkgname = "pkg-config"
pkgver = "0.29.2"
pkgrel = 0
pkgdesc = "pkg-config is a helper tool used when compiling applications and libraries."
url = "https://www.freedesktop.org/wiki/Software/pkg-config/"
arch = "x86_64"
license = "GPLv2 or later"

sources = [f"https://{pkgname}.freedesktop.org/releases/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ['6fc69c01688c9458a57eb9a1664c9aba372ccda420a02bf4429fe610e7e7d591']
depends = ['glib']

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(f"{c.SRCDIR}/configure")
  c.sh("make",f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
