recipever = 0
pkgname = "file"
pkgver = "5.48"
actualver = f"FILE{pkgver.replace(".","_")}" #thanks, wonderful file(1) devs
pkgrel = 0
pkgdesc = "An implementation of the Unix File(1) command."
url = "https://www.darwinsys.com/file/"
arch = "x86_64"
license = "BSD-2-Clause-Darwin"


sources = [f"https://github.com/{pkgname}/{pkgname}/archive/refs/tags/{actualver}.tar.gz"]
sha256sum = ["76cefc3a662ab0e9f45db941b0a56e71705abad0690da19a5c32379cc6de3488"]
depends = ["bzip", "glibc", "libseccomp", "xz", "zlib", "zstd"]
makedepends=["git"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{actualver}" # TODO fix this is because tar files have a top level name
  c.sh("autoreconf -fi")
  c.sh("./configure")

  c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
