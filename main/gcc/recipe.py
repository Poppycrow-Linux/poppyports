recipever = 0
pkgname = "gcc"
pkgver = "16.1.0"
pkgrel = 0
pkgdesc = "GNU Compiler Collection"
url = "https://gcc.gnu.org/"
arch = "x86_64"
license = "GPL v3"

sbu = 18.0

sources = [f"https://ftpmirror.gnu.org/gcc/gcc-{pkgver}/gcc-{pkgver}.tar.xz"]
depends = ["gmp", "mpfr", "mpc", "isl", "zlib"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.env["CC"] = "gcc"
  c.env["CXX"] = "g++"

  c.sh("mkdir", "-p", c.SRCDIR + "/build")
  c.SRCDIR = c.SRCDIR + "/build"

  c.sh("../configure",
       "--prefix=/usr",
       "--with-system-zlib",
       "--enable-default-pie",
       "--enable-default-ssp",
       "--enable-host-pie",
       "--disable-fixincludes",
       "--enable-languages=c,c++")

  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
