recipever = 0
pkgname = "udev"
pkgver = "261.1"
pkgrel = 0
pkgdesc = "Udev extracted from systemd"
url = "https://github.com/systemd/systemd"
arch = "x86_64"
license = "LGPL-2.1-or-later"

sources = [f"https://github.com/systemd/systemd/archive/refs/tags/v{pkgver}.tar.gz"]
depends = []

def build(c):
    c.SRCDIR = c.SRCDIR + f"/systemd-{pkgver}"
    c.env["CC"] = "gcc"
    c.env["CXX"] = "g++"

    c.sh("sed", "-e", "s/GROUP=\"render\"/GROUP=\"video\"/",
         "-e", "s/GROUP=\"sgx\", //",
         "-i", f"{c.SRCDIR}/rules.d/50-udev-default.rules.in")
    c.sh("sed", "-i", "/systemd-sysctl/s/^/#/",
         f"{c.SRCDIR}/rules.d/99-systemd.rules.in")
    c.sh("sed", "-e", "/NETWORK_DIRS/s/systemd/udev/",
         "-i", f"{c.SRCDIR}/src/libsystemd/sd-network/network-util.h")

    builddir = f"{c.SRCDIR}/build"
    c.sh("mkdir", "-p", builddir)

    c.sh(
        "meson", "setup", builddir,
        c.SRCDIR,
        "--prefix=/usr",
        "--buildtype=release",
        "-Dmode=release",
        "-Ddev-kvm-mode=0660",
        "-Dlink-udev-shared=false",
        "-Dlogind=false",
        "-Dvconsole=false",
    )

    c.sh(f"""bash (grep "'name' :" {c.SRCDIR}/src/udev/meson.build | awk '{{print $3}}' | tr -d ",'" | grep -v 'udevadm') &&
    ninja udevadm systemd-hwdb $(ninja -n | grep -Eo '(src/(lib)?udev|rules.d|hwdb.d)/[^ ]*') $(realpath libudev.so --relative-to .) > {builddir}/udev_helpers.txt
        """, shell = True, cwd=builddir)

    c.sh(
        "bash", "-lc",
        f"""
        cd {builddir} &&
        udev_helpers=$(grep "'name' :" {c.SRCDIR}/src/udev/meson.build | awk '{{print $3}}' | tr -d ",'" | grep -v 'udevadm') &&
        ninja udevadm systemd-hwdb $(ninja -n | grep -Eo '(src/(lib)?udev|rules.d|hwdb.d)/[^ ]*') $(realpath libudev.so --relative-to .) $udev_helpers
        """, shell = True
    )



def install(c):
    builddir = f"{c.SRCDIR}/build"
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/bin")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/sbin")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/lib/udev/hwdb.d")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/lib/udev/rules.d")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/lib/udev/network")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/lib/pkgconfig")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/share/pkgconfig")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/include")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/usr/lib/udev")
    c.sh("install", "-vm755", "-d", f"{c.PKGDIR}/etc/udev")

    c.sh("install", "-vm755", f"{builddir}/udevadm", f"{c.PKGDIR}/usr/bin/")
    c.sh("install", "-vm755", f"{builddir}/systemd-hwdb", f"{c.PKGDIR}/usr/bin/udev-hwdb")
    c.sh("ln", "-svfn", "../bin/udevadm", f"{c.PKGDIR}/usr/sbin/udevd")
    c.sh("cp", "-av", f"{builddir}/libudev.so", f"{c.PKGDIR}/usr/lib/")
    c.sh("cp", "-av", f"{builddir}/libudev.so.*", f"{c.PKGDIR}/usr/lib/", shell = True)
    #c.sh("cp", "-av", f"{builddir}/libudev.so{,*[0-9]}", f"{c.PKGDIR}/usr/lib/")
    c.sh("install", "-vm644", f"{c.SRCDIR}/src/libudev/libudev.h", f"{c.PKGDIR}/usr/include/", shell = True)
    c.sh("install", "-vm644", f"{builddir}/src/libudev/*.pc", f"{c.PKGDIR}/usr/lib/pkgconfig/", shell = True)
    c.sh("install", "-vm644", f"{builddir}/src/udev/*.pc", f"{c.PKGDIR}/usr/share/pkgconfig/", shell = True)
    c.sh("install", "-vm644", f"{c.SRCDIR}/src/udev/udev.conf", f"{c.PKGDIR}/etc/udev/", shell = True)
    c.sh("install", "-vm644", f"{c.SRCDIR}/rules.d/*", f"{c.PKGDIR}/usr/lib/udev/rules.d/", shell = True)
    c.sh("install", "-vm644", f"{c.SRCDIR}/hwdb.d/*", f"{c.PKGDIR}/usr/lib/udev/hwdb.d/", shell = True)
    c.sh("install", "-vm755", "$udev_helpers", f"{c.PKGDIR}/usr/lib/udev", shell = True)
    c.sh("install", "-vm644", f"{c.SRCDIR}/network/99-default.link", f"{c.PKGDIR}/usr/lib/udev/network")
