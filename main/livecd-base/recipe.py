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
    "main/busybox",
    "main/dinit-poppy",
    "main/glibc",
    "main/bash",
    "apps/figlet",
    "apps/fastfetch",
    "main/apk-tools",
    "main/ncurses",
    "main/udev",
    "main/zlib",
    "main/e2fsprogs",
    "main/dinit",
    "main/dinit-tiny-devd",
    "main/openssl",
    "main/libstdc++-v3",
    "apps/parted",
    "main/libcap"
]


def build(c):
    pass


def install(c):
    c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init")  # make init executable
    c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
