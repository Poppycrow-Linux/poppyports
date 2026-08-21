# what the fuck would the convention for make be because theres also say bsdmake should this be gmake?? thoughts?
pkgname = "cmake"
pkgver = "4.4.2"
pkgrel = 0
pkgdesc = "CMake Utility"
url = "https://cmake.org/"
arch = "x86_64"
license = "BSD-3-Clause"


sources = [f"https://github.com/Kitware/CMake/releases/download/v4.4.2/{pkgname}-{pkgver}.tar.gz"]
depends = ["libc"]
makedepends = ["make"]


def build(c):
  c.SRCDIR += f"/{pkgname}-{pkgver}"
  c.sh("mkdir -p build")
  c.sh(f"../bootstrap --parallel={c.NPROC}", cwd=f"{c.SRCDIR}/build") #TODO: make it use system libraries once we get sysroot going
  c.sh("make", f"-j{c.NPROC}", cwd=f"{c.SRCDIR}/build")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}", cwd=f"{c.SRCDIR}/build")
