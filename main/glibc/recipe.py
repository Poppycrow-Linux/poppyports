# NOTE: whatever glibc we're building is shipping a ton of shit, i guess were building for debug? idk
recipever = 0
pkgname = "glibc"
pkgver = "2.42"
pkgrel = 0
pkgdesc = "GNU libc"
url = "https://gnu.org/"
arch = "x86_64"
license = "GPL v2"

sbu = 13.2

# the reason 2.42 is used rn is because this is the one debian has and links with for me
sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.env["CC"] = "gcc"
  c.env["CXX"] = "g++"

  # apply patches
  c.sh("patch", "-p1", "-i", c.PORTDIR + "/001-fix-sysmount.patch")

  # because you cannot do in tree builds gnu fuck you
  c.sh("mkdir", "-p", c.SRCDIR + "/build")
  c.SRCDIR = c.SRCDIR + "/build"

  c.sh("../configure", "--prefix=/usr")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
