recipever = 0
pkgname = "dinit-poppy"
pkgver = "0.99.24"
pkgrel = 0
pkgdesc = "Collection of dinit services, forked from dinit-chimera."
url = "https://codeberg.org/Poppycrow-Linux/dinit-poppy"
arch = "x86_64"
license = "BSD-Clause-2 Simplified"


# https://codeberg.org/Poppycrow-Linux/dinit-poppy/archive/v0.99.24.tar.gz
sources = [f"{url}/archive/v{pkgver}.tar.gz"]
depends = ["libstdc++", "dinit"]
makedepends = ["meson"]


def build(c):
    c.SRCDIR = (
        c.SRCDIR + f"/{pkgname}"
    )  # TODO fix this is because tar files have a top level name
    global bdir
    bdir = c.SRCDIR + "/build"
    c.sh("meson", "build/")

    c.sh("ninja", "all", cwd=bdir)
    # i feel like this should be something else?
    # it's not really a part of installation process and moreso prep work but doesn't fit into prepare chronologically either
    # TODO: acutally use my free will as a fork and add a meson install or something?
    c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib")
    c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib/dinit.d")
    c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib/dinit.d/early")


# who loves cherrypicking?
def install(c):
    c.sh(f"cp -r {bdir}/early/scripts/init {c.PKGDIR}/init")
    c.sh(f"chmod +x {c.PKGDIR}/init")
    c.sh(f"cp -r {bdir}/services/* {c.PKGDIR}/usr/lib/dinit.d")
    c.sh(f"cp -r {bdir}/early/ {c.PKGDIR}/usr/lib/dinit.d/")
