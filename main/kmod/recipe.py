recipever = 0
pkgname = "kmod"
pkgver = "32"
pkgrel = 0
pkgdesc = "Linux kernel module management utilities and library (libkmod)"
url = "https://git.kernel.org/pub/scm/utils/kernel/kmod/kmod.git"
arch = "x86_64"
license = "LGPL-2.1-or-later AND GPL-2.0-or-later"

sources = [f"https://mirrors.edge.kernel.org/pub/linux/utils/kernel/kmod/{pkgname}-{pkgver}.tar.xz"]
depends = ["xz", "zlib"] # needed COMPRESSED modules

def build(c):
    c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"

    c.sh(
        "./configure",
        "--prefix=/usr",
        "--sysconfdir=/etc",
        "--bindir=/usr/bin",
        "--libdir=/usr/lib",
        "--with-xz",
        "--with-zlib",
        f"CFLAGS={c.CFLAGS}",
        f"LDFLAGS={c.LDFLAGS}"
    )

    c.sh("make", f"-j{c.NPROC}")

def install(c):
    c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
