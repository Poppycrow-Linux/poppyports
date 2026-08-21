pkgname = "sysroot-base"
pkgver = "0.0.1"
pkgrel = 0
pkgdesc = "Poppycrow sysroot system package"
url = "https://www.poppycrow.org/"
arch = "x86_64"
license = "BSD3"
sources = []

depends = [
    "main/bash",
    "main/gcc", #libstdc++ is not included since it is a part of gcc
    "main/chimerautils",
    "main/ncurses",
    "main/libedit",
    "main/linux-pam",
    "main/bzip2",
    "main/pcre2",
    "main/gdbm",
    "main/readline",
    "main/apk-tools",
    "main/ncurses",
    "main/zlib",
    "main/xz",
    "main/make",
    "main/muon",
    "main/muon-meson-compat",
    "main/ninja",
    "lang/python3",
    "main/openssl",
    "main/libcap",
    "main/acl",
    "main/glibc",
    "main/libdinitctl",
]


def build(c):
    pass


def install(c):
   c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
