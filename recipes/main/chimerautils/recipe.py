import os # this is gross but i need it
recipever = 0
pkgname = "chimerautils"
pkgver = "15.0.3_git20260818"
commit = "8a71251d1846185899600a7484ac0f522dea8740"
pkgrel = 0
pkgdesc = "Alternative to GNU coreutils (and more) using software from FreeBSD"
url = "https://github.com/chimera-linux/chimerautils"
arch = "x86_64"
license = "BSD-2-Clause"


sources = [f"{url}/archive/{commit}.tar.gz"]
depends = ["libc", "libxo", "libedit", "ncurses", "openssl"]
makedepends = ['byacc', 'meson', "ninja"]


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{commit}"
  c.sh("meson", "setup", "build/")
  c.sh("ninja","-C","build/")

def install(c):
    bindir = f"{c.PKGDIR}/bin"
    os.makedirs(bindir, exist_ok=True)

    for srcdir in ("src.freebsd", "src.custom", "src.freebsd/miscutils", "src.freebsd/coreutils", "src.freebsd/findutils", "src.freebsd/diffutils", ):
        root = f"{c.SRCDIR}/build/{srcdir}"

        if not os.path.isdir(root):
            continue

        for utility in os.listdir(root):
            utility_path = f"{root}/{utility}/{utility}"

            if os.path.isfile(utility_path) and os.access(utility_path, os.X_OK):
                c.cp(utility_path, f"{bindir}/{utility}")
