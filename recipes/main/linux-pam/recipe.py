recipever = 0
pkgname = "linux-pam"
pkgver = "1.7.2"
pkgrel = 0

pkgdesc = "Pluggable Authentication Modules for Linux"
url = "https://github.com/linux-pam/linux-pam"
arch = "x86_64"
license = "BSD-3-Clause"

sources = [f"{url}/releases/download/v{pkgver}/Linux-PAM-{pkgver}.tar.xz"]
sha256 = "3d86b6383fb5fd9eb9578d2cd47d92801191f4bf3f9bc61419bfefc8aa1e531a"

depends = ["linux-pam-base"]
makedepends = ["flex-devel-static", "gettext-devel", "linux-headers"]
hostmakedepends = ["docbook-xsl", "gettext-devel", "libxslt-progs", "meson", "pkgconf"]

options = ["linkundefver"]


def build(c):
    c.SRCDIR = c.SRCDIR + f"/Linux-PAM-{pkgver}"
    c.sh("meson", "setup", "build", "-Ddocdir=/usr/share/doc/pam", "-Dnis=disabled", "-Daudit=disabled", "-Dselinux=disabled", "-Dvendordir=/usr/share/pam", "")
    c.sh("meson", "compile", "-C", "build")


def install(c):
    libdir = f"{c.PKGDIR}/usr/lib"

    c.sh("meson", "install", "-C", "build", "--destdir", c.PKGDIR)
    c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/share/licenses/{pkgname}", libdir)

    c.cp(f"{c.SRCDIR}/COPYING", f"{c.PKGDIR}/usr/share/licenses/{pkgname}/COPYING")
    c.sh(f"cp -r {c.SRCDIR}/build/libpam/libpam.* {libdir}", shell = True)

    c.sh("chmod", "4755", f"{c.PKGDIR}/usr/sbin/unix_chkpwd")
    c.sh("rm", "-rf", f"{c.PKGDIR}/usr/lib/systemd")
