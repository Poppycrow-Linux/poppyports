recipever = 0
pkgname = "libstdc++-v3"
pkgver = "16.1.0"
pkgrel = 0
pkgdesc = "libstdc++ V3, part of GCC sources"
url = "https://gcc.gnu.org/"
arch = "x86_64"
license = "GPL v3"

sbu = 18.0

sources = [f"https://ftpmirror.gnu.org/gcc/gcc-{pkgver}/gcc-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/gcc-{pkgver}"

  c.sh("mkdir", "-p", c.SRCDIR + "/build")
  c.SRCDIR = c.SRCDIR + "/build"

  c.sh("../libstdc++-v3/configure",
       "--prefix=/usr",
       "--disable-nls",
       "--disable-fixincludes",
       "--enable-multilib", # this is for 32 bit apps to work hopefully I guess
       "--disable-libstdcxx-pch")

  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
