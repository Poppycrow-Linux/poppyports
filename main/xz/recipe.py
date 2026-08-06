pkgname = "xz"
pkgver = "5.8.3"
pkgrel = 0
pkgdesc = "XZ utils"
url = "https://tukaani.org/xz"
arch = "x86_64"
license = "GPL-2.0-or-later AND 0BSD AND LicenseRef-Public-Domain AND LGPL-2.1-or-later"
#maintainer = "cachewave" this is pointless. everyone should be able to update whatever packages need to be done

sources = [f"https://github.com/tukaani-project/xz/releases/download/v{pkgver}/xz-{pkgver}.tar.xz"]
depends = ["libc"]


def build(c):
  c.SRCDIR += f"/xz-{pkgver}"
  c.sh("./configure", "--disable-doc", "--prefix=/usr") #fix /usr/local nonsense
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
