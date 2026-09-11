pkgname = "zlib"
pkgver = "1.3.2"
pkgrel = 0
pkgdesc = "a free, general-purpose, lossless data-compression library for use on virtually any computer hardware and operating system"
url = "https://zlib.net/"
arch = "x86_64"
license = "zlib"
maintainer = "samxyz30"
recipever = 1

build_wrksrc = f"{pkgname}-{pkgver}"
build_style = "gnu_configure"
sources = [f"https://zlib.net/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ["bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16"]
depends = ["libc"]

make_check = False
