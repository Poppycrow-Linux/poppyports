pkgname = "hello"
pkgver = "2.12.1"
pkgrel = 0
recipever = 1 ## this is not enforced anywhere but if you use buildstyles then PLEASE make this one
pkgdesc = "Print a friendly greeting"
url = "https://www.gnu.org/software/hello/"
arch = ["x86_64", "aarch64"]
license = "GPL-3.0-or-later"

sources = [f"https://ftp.gnu.org/gnu/{pkgname}/{pkgname}-{pkgver}.tar.gz",]


depends = ["libc"]
makedepends = ["make", "sed"]

build_style = "gnu_configure"
build_wrksrc = f"{pkgname}-{pkgver}"

configure_args = [
  "--disable-nls",
]

# The target binary cannot run natively during a cross build.
make_check = False
