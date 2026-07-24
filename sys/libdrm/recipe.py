recipever = 0
pkgname = "libdrm"
pkgver = "2.4.133"
pkgrel = 0
pkgdesc = "Userspace interface to kernel DRM services"
url = "https://dri.freedesktop.org"
arch = "x86_64"
license = "MIT"

sbu = 0.1

yuck = "libdrm-libdrm-2.4.133-cb4669afe87470752643f46c81bddb45b0db48e4" ## TODO: fix this hardcoding thing

sources = [f"https://gitlab.freedesktop.org/mesa/drm/-/archive/libdrm-{pkgver}/drm-libdrm-{pkgver}.tar.gz"]
sha256sum = ["c2a323e050cdac4aca5e1ec5702ffc65f26ac0c38980dd1fd5d8dc7e1eecdf9c"]

depends = ["udev-devel", "libpciaccess-devel", "linux-headers"]
makedepends = ["meson", "pkgconf"]


def build(c):
    c.SRCDIR = c.SRCDIR + f"/{yuck}"
    c.sh(
        "meson", "setup", f"{c.SRCDIR}", f"build/",
        f"--prefix={c.PKGDIR}/usr",
        "-Dudev=true",
        "-Dvalgrind=disabled",
        "--reconfigure"
    )
    c.sh("ninja", "-C", f"build/")


def install(c):
    c.sh("ninja", "-C", f"build/", "install")
