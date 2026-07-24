pkgname = "openssl"
pkgver = "3.5.7"
pkgrel = 0
pkgdesc = "Library for various kinds of cryptography"
url = "openssl-library.org"
arch = "x86_64"
license = "apache-2.0"

sources = [f"https://github.com/openssl/openssl/releases/download/openssl-{pkgver}/openssl-{pkgver}.tar.gz"]
depends = []

def build(c):
  c.SRCDIR += f"/openssl-{pkgver}"
  c.sh("./Configure", f"--prefix={c.PKGDIR}/usr")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install")
