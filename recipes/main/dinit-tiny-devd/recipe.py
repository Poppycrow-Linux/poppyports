recipever = 0
pkgname = "dinit-tiny-devd"
pkgver = "0.99.24"
pkgrel = 0
pkgdesc = "Tiny shell script that provides /usr/libexec/dinit-devd for dinit-poppy"
url = "https://codeberg.org/Poppycrow-Linux/dinit-poppy"
arch = "x86_64"
license = "BSD-Clause-2 Simplified"
provides = ["dinit-devd"]

# https://codeberg.org/Poppycrow-Linux/dinit-poppy/archive/v0.99.24.tar.gz
sources = []  # downloading a bash script that's gonna be in the folder right next to the recipe is excessive
depends = ["dinit-poppy", "udev"]  # TECHNICALLY this script does not need dinit BUT it's gonna get pulled as a dep of dinit-poppy anyways
makedepends = ["meson"]


def build(c):
   pass # we are not building anything



def install(c):
    c.sh("chmod", "+x", f"{c.PORTDIR}/dinit-devd") # make it executable
    c.sh(f"mkdir -p {c.PKGDIR}/usr/libexec/") # make the dir
    c.cp(f"{c.PORTDIR}/dinit-devd", f"{c.PKGDIR}/usr/libexec/")
