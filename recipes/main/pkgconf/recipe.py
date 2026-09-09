pkgname = "pkgconf"
pkgver = "3.0.7"
pkgrel = 0
pkgdesc = "Lightweight pkg-config compatible tool"
url = "https://github.com/pkgconf/pkgconf"
arch = "x86_64"
license = "ISC"

sources = [f"{url}/releases/download/{pkgname}-{pkgver}/{pkgname}-{pkgver}.tar.xz",]


depends = ["libc"]
build_style = "gnu_configure"
build_wrksrc = f"{pkgname}-{pkgver}"

make_check = False

configure_args = [
    "--prefix=/usr",
    "--disable-static",
    "--enable-shared",
    "--libdir=/usr/lib"
]
