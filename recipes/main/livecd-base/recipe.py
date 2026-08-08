pkgname = "livecd-base"
pkgver = "0.0.1"
pkgrel = 0
pkgdesc = "Poppycrow livecd system package"
url = "https://www.poppycrow.org/"
arch = "x86_64"
license = "BSD3"
sources = []

depends = [
    "main/linux-stable",
    "main/libstdc++-v3",
    "main/libgcc",
    "main/busybox",
    "main/dinit-poppy",
    "main/glibc",
    "main/bash",
    "apps/figlet",
    "apps/fastfetch",
    "main/apk-tools",
    "main/sd-tools",
    "main/ncurses",
    "main/udev",
    "main/zlib",
    "main/e2fsprogs",
    "main/dinit",
    "main/xz",
    "main/nyagetty",
    "main/dinit-tiny-devd",
    "main/openssl",
    "apps/parted",
    "main/libcap",
    "main/acl",
    "main/nyagetty-dinit",
    "main/kmod"
]


def build(c):
    pass


def install(c):
   c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init")  # make init executable
   c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
