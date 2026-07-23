recipever = 0
pkgname = "libffi"
pkgver = "3.7.1"
pkgrel = 0
pkgdesc = "The libffi library provides a portable, high level programming interface to various calling conventions. This allows a programmer to call any function specified by a call interface description at run-time."
url = "https://github.com/libffi/libffi"
arch = "x86_64"
license = "https://github.com/libffi/libffi/blob/master/LICENSE"

sbu = 0.3

sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
sha256sum = ['df80a3ff1d3421ac2ae0e368575f82f30383f932481ecf2dd1d5f7f88c92f547']
depends = ["glibc"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh(f"{c.SRCDIR}/autogen.sh")
  c.sh(f"{c.SRCDIR}/configure", "--prefix=/usr/local", "--enable-shared")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")
