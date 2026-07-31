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

    # remove the groups because lfs told us so
    c.sh("sed", "-i",
         "-e", "s/GROUP=\"render\"/GROUP=\"video\"/",
         "-e", "s/GROUP=\"sgx\", //",
         "rules.d/50-udev-default.rules.in")

    # 2. more systemd bullshit
    c.sh("sed", "-i", "/systemd-sysctl/s/^/#/", "rules.d/99-systemd.rules.in")

    # 3. we don't need systemd vconsole!! fuck off!!!'
    c.sh("rm", "-f", "rules.d/90-vconsole.rules")

    meson_args = [
        "--prefix=/usr",
        "--sysconfdir=/etc",
        "--buildtype=release",
        "-Dmode=release",
        "-Ddev-kvm-mode=0660",        # LFS security override for kvm group
        "-Dlink-udev-shared=false",   # We don't need a systemd shared libary!! fuck off!'
        "-Dstandalone-binaries=true",
        "-Dsysusers=false",
        "-Dtmpfiles=false",
        "-Dhwdb=true",
        # Disable all other systemd components. some options have disabled because otherwise it goes # DEPRECATION!!! false was replaced by disabled for no reason fuck you.
        "-Dbootloader=disabled",
        "-Dlogind=false",
        "-Dnetworkd=false",
        "-Dtimesyncd=false",
        "-Dmachined=false",
        "-Dimportd=disabled",
        "-Dhostnamed=false",
        "-Dtimedated=false",
        "-Dlocaled=false",
        "-Dcoredump=false",
        "-Dinitrd=false",
        "-Dhibernate=false",
        "-Dpam=disabled",
        "-Dselinux=disabled",
        "-Dpolkit=disabled",
        "-Dbacklight=false",
        "-Drfkill=false",
        "-Dpasswdqc=disabled",
        "-Dvconsole=false",
        "-Dquotacheck=false",
        "-Dldconfig=false",
        "-Dman=disabled"
    ]

    c.sh("meson", "setup", "build", *meson_args)

    c.sh("ninja", "-C", "build", "udevadm", "systemd-hwdb", f"-j{c.NPROC}")


def install(c):
    stage_dir = f"{c.SRCDIR}/_install_stage"
    c.env["DESTDIR"] = stage_dir

    # quantum we do not dump shit in tmp we do this in srcdir so it gets removed at some point ok????
    c.sh("ninja", "-C", "build", "install")

    c.sh("mkdir", "-p",
         f"{c.PKGDIR}/usr/bin",
         f"{c.PKGDIR}/usr/lib/pkgconfig",
         f"{c.PKGDIR}/usr/include"
    )

    # WE LOVE CHERRY PICKING!!!!
    c.sh(f"cp -a {stage_dir}/usr/bin/udevadm {c.PKGDIR}/usr/bin/", shell=True)
    c.sh(f"cp -a {stage_dir}/usr/bin/systemd-hwdb {c.PKGDIR}/usr/bin/ || true", shell=True) # hwdb binary

    c.sh(f"cp -a {stage_dir}/usr/lib/libudev.so* {c.PKGDIR}/usr/lib/", shell=True)
    c.sh(f"cp -a {stage_dir}/usr/include/libudev.h {c.PKGDIR}/usr/include/", shell=True)
    c.sh(f"cp -a {stage_dir}/usr/lib/pkgconfig/libudev.pc {c.PKGDIR}/usr/lib/pkgconfig/", shell=True)

    # udev rule number 1: udev has no rules. actually wait it does, let's copy them over.'
    c.sh(f"[ -d {stage_dir}/usr/lib/udev ] && cp -a {stage_dir}/usr/lib/udev {c.PKGDIR}/usr/lib/ || true", shell=True)
    c.sh(f"[ -d {stage_dir}/etc/udev ] && cp -a {stage_dir}/etc/udev {c.PKGDIR}/etc/ || true", shell=True)
