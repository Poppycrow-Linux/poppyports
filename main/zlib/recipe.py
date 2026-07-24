pkgname = "zlib"
pkgver = "1.3.2"
pkgrel = 0
pkgdesc = "a free, general-purpose, lossless data-compression library for use on virtually any computer hardware and operating system"
url = "https://zlib.net/"
arch = "x86_64"
license = "zlib"
maintainer = "samxyz30"

sources = [f"https://zlib.net/zlib-{pkgver}.tar.gz"]
sha256sum = ["bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16"]
depends = []

def build(c):
  c.SRCDIR += f"/zlib-{pkgver}"
  c.sh("./configure", "--prefix=/usr")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}/usr")
