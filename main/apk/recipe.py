recipever = 0
pkgname = "apk-tools"
pkgver = "3.0.6"
pkgrel = 0
pkgdesc = "Alpine Package Keeper (apk) is a package manager originally built for Alpine Linux, but now used by several other distributions as well."
url = "https://gitlab.alpinelinux.org/alpine/apk-tools"
arch = "x86_64"
license = "GPLv2"

# https://gitlab.alpinelinux.org/alpine/apk-tools/-/archive/v3.0.6/apk-tools-v3.0.6.tar.gz
sources = [f"{url}/-/archive/v{pkgver}/{pkgname}-v{pkgver}.tar.gz"]
sha256sum = ["e9b62742ef7e9e8c1c051efdaed3a2f49d06d8ce20c707697aa23d29bbc7c86a"]
depends = []
makedepends = ['meson', 'python', 'ninja']


def build(c):
# meson setup -Dprefix=/ build
# ninja -C build
# meson install -C build

  c.SRCDIR = c.SRCDIR + f"/{pkgname}-v{pkgver}"
  c.sh("meson", "setup", f"-Dprefix={c.PKGDIR}", "-Dzstd=disabled", "build/")
  c.sh("ninja", "-C", "build/")
  ####c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("meson", "install", "-C", "build/")
  #c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
