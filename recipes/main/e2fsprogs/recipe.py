recipever = 0
pkgname = "e2fsprogs"
pkgver = "1.47.4"
pkgrel = 0
pkgdesc = "Standard utilities for creating, fixing, configuring, and debugging ext2/3/4 filesystems"
url = "http://e2fsprogs.sourceforge.net"
arch = "x86_64"
license = "GPL-2.0-only"

sources = [f"https://mirrors.edge.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/v{pkgver}/e2fsprogs-{pkgver}.tar.xz"]
depends = ["util-linux"] # libuuid and libblkid are from util-linux. cachewave you are an idot e2fs progs does not provide them!!

def build(c):
    c.SRCDIR = c.SRCDIR + f"/e2fsprogs-{pkgver}"
    c.env["CC"] = "gcc"
    c.env["CXX"] = "g++"

    # disable poop that's provided by util linux
    configure_args = [
        "--prefix=/usr",
        "--sysconfdir=/etc",
        "--enable-elf-shlibs",
        "--disable-libblkid",
        "--disable-libuuid",
        "--disable-uuidd",
        "--disable-fsck"
    ]

    c.sh("./configure", *configure_args)
    c.sh("make", f"-j{c.NPROC}")


def install(c):
    c.env["DESTDIR"] = c.PKGDIR
    c.sh("make", "install")

    # libraries are a separate make thing for no reason
    c.sh("make", "install-libs")

   # no man files, no info dir. no fluf no theory crazy style.
    c.sh("rm", "-f", f"{c.PKGDIR}/usr/share/info/dir")
