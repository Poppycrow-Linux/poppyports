recipever = 1
pkgname = "chimerautils"
pkgver = "15.0.3_git20260818"
commit = "8a71251d1846185899600a7484ac0f522dea8740"
pkgrel = 0
pkgdesc = "Alternative to GNU coreutils (and more) using software from FreeBSD"
url = "https://github.com/chimera-linux/chimerautils"
arch = "x86_64"
license = "BSD-2-Clause"

build_wrksrc = f"{pkgname}-{commit}"
build_style = "meson"
sources = [f"{url}/archive/{commit}.tar.gz"]
depends = ["libc", "libxo", "libedit", "ncurses", "openssl"]
makedepends = ['byacc', 'meson', "ninja"]
