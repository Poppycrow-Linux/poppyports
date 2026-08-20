pkgname = "bzip2"
pkgver = "1.0.8"
pkgrel = 0
pkgdesc = "A high-quality data compression program"
url = "https://sourceware.org/bzip2/"
arch = "x86_64"
license = "BSD"


sources = [f"https://sourceware.org/pub/{pkgname}/{pkgname}-{pkgver}.tar.gz"]
depends = ["libc", 'sh']
makedepends = ['sed']


def build(c):
  c.SRCDIR += f"/{pkgname}-{pkgver}"
  c.sh(f"make -j{c.NPROC} -f Makefile-libbz2_so")
  c.sh(f"make -j{c.NPROC} bzip2 bzip2recover")


def install(c):
    for d in [
        "usr/bin",
        "usr/lib",
        "usr/include",
        "usr/share/man/man1",
        "usr/lib/pkgconfig",
        f"usr/share/licenses/{pkgname}",
  ]:
        c.sh(f"install -dm755 {c.PKGDIR}/{d}")

    c.sh(f"install -m755 bzip2-shared {c.PKGDIR}/usr/bin/bzip2")
    c.sh(f"install -m755 bzip2recover bzdiff bzgrep bzmore {c.PKGDIR}/usr/bin")

    for link in ["bunzip2", "bzcat"]:
        c.sh(f"ln -sf bzip2 {c.PKGDIR}/usr/bin/{link}")

    c.sh(f"cp -a libbz2.so* {c.PKGDIR}/usr/lib")
    for link in ["libbz2.so", "libbz2.so.1"]:
        target = f"libbz2.so.{pkgver}"
        c.sh(f"ln -s {target} {c.PKGDIR}/usr/lib/{link}")

    c.sh(f"install -m644 bzlib.h {c.PKGDIR}/usr/include/")
    c.sh(f"install -m644 bzip2.1 {c.PKGDIR}/usr/share/man/man1/")
    for link in ["bunzip2.1", "bzcat.1", "bzip2recover.1"]:
        c.sh(f"ln -sf bzip2.1 {c.PKGDIR}/usr/share/man/man1/{link}")

    c.sh(f"install -Dm644 {c.PORTDIR}/bzip2.pc {c.PKGDIR}/usr/lib/pkgconfig/bzip2.pc")
    c.sh(f'sed "s|@VERSION@|{pkgver}|" -i {c.PKGDIR}/usr/lib/pkgconfig/bzip2.pc')
    c.sh(f"install -Dm644 LICENSE {c.PKGDIR}/usr/share/licenses/{pkgname}/LICENSE")
