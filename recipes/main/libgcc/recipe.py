## TODO: make this a subpackage of gcc to not build the gcc twice!!!

recipever = 0
pkgname = "libgcc"
pkgver = "16.1.0"
pkgrel = 0
pkgdesc = "LIB gcc"
url = "https://gcc.gnu.org/"
arch = "x86_64"
license = "GPL v3"

# http://gcc.cybermirror.org
# https://ftpmirror.gnu.org
# sources = [f"https://ftpmirror.gnu.org/gcc/gcc-{pkgver}/gcc-{pkgver}.tar.xz"]
sources = [f"https://ftp.gwdg.de/pub/misc/gcc/releases//gcc-{pkgver}/gcc-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.env["CC"] = "gcc"
  c.env["CXX"] = "g++"
  c.SRCDIR = c.SRCDIR + f"/gcc-{pkgver}"
  c.sh("mkdir", "-p", c.SRCDIR + "/build")
  c.SRCDIR = c.SRCDIR + "/build"
  c.sh("echo $CC")
  c.sh("../configure",
       "--prefix=/usr",
       "--disable-nls",
       "--disable-fixincludes",
       "--enable-multilib", # this is for 32 bit apps to work hopefully I guess
       "--disable-libstdcxx-pch")
  c.sh(f"make all-gcc -j{c.NPROC}") # this is needed because libgcc is STUPID and needs libgcc
  c.sh("make", "all-target-libgcc", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install-target-libgcc", f"DESTDIR={c.PKGDIR}")
