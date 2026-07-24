recipever = 0
pkgname = "libwacom"
pkgver = "2.19.1"
pkgrel = 0
pkgdesc = "libwacom is a library to identify graphics tablets and their model-specific \
features. It provides easy access to information such as \"is this a built-in \
on-screen tablet\", \"what is the size of this model\", etc. \
"
url = "https://linuxwacom.github.io/libwacom/"
arch = "x86_64"
license = "MIT"

sbu = 0.1

sources = [f"https://github.com/linuxwacom/libwacom/releases/download/{pkgname}-{pkgver}/{pkgname}-{pkgver}.tar.xz"]
sha256sum = ["a1e5b1e7ef60fa70ed05b55d888d980ec7e86bd15594857f3c48c529b661bf32"]
depends = []


def build(c):
  
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  # tests are disabled because they require python-libevdev and pyudev
  c.sh("meson","setup","-D","tests=disabled",f"--prefix={c.PKGDIR}/usr", f"build/")
  c.sh("ninja", "-C", f"build/")

def install(c):
  c.sh("ninja", "-C", f"build/", "install")
