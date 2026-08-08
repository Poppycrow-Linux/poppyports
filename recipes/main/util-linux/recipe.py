pkgname = "util-linux"
pkgver = "2.42.2"
pkgrel = 0
pkgdesc = "util-linux is a package of utilities distributed by the Linux Kernel Organization for use in a Linux operating system."
url = "https://www.kernel.org/pub/linux/utils/util-linux/"
arch = "all"
license = "GPLv2"

sources = [f"https://www.kernel.org/pub/linux/utils/util-linux/v2.42/util-linux-{pkgver}.tar.xz"]
depends = ["libc"]

def build(c):
  c.SRCDIR += f"/util-linux-{pkgver}"
  c.sh("./configure", 
    "--bindir=/usr/bin", "--libdir=/usr/lib", "--runstatedir=/run", "--sbindir=/usr/sbin",
    "--disable-chfn-chsh",
    "--disable-static",
    "--without-systemd",
    "--without-systemdsystemunitdir"
  )
  
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
