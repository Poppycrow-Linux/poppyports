pkgname = "linux-stable-headers"
pkgver = "7.2.2"
pkgrel = 0
pkgdesc = "Linux userspace kernel headers"
url = "https://www.kernel.org/"
arch = ["x86_64", "aarch64", "armv7", "i686", "riscv64", "ppc64le", "s390x"]
license = "GPL-2.0-only"

sources = [
  f"https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-{pkgver}.tar.xz",
]

depends = ["libc"]
makedepends = ["make"]

build_style = "kernel_headers"
build_wrksrc = f"linux-{pkgver}"
