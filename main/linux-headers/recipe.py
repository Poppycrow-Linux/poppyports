recipever = 0
pkgname = "linux-headers"
pkgver = "7.1.4"
pkgrel = 0
pkgdesc = "Headers for the Linux kernel"
url = "https://www.kernel.org/"
arch = "all"
license = "GPL"

sources = ["https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-7.1.4.tar.xz"]
sha256sum = ["1c63922a119675d38e3ae0f8f6ee07f15c41a786ab9ed66563749bb8c9a08e2e"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + "/linux-7.1.4"  # TODO fix this is because tar files have a top level name
  c.sh("make", "mrproper") # TODO Move to a prepare() !!!

def install(c):
  c.sh("make", "headers_install", f"INSTALL_HDR_PATH={c.PKGDIR}/usr")

