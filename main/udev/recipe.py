recipever = 0
pkgname = "udev"
pkgver = "261.1"
pkgrel = 0
pkgdesc = "Udev from systemd without systemd"
url = "https://github.com/systemd/systemd"
arch = "x86_64"
license = "LGPL-2.1-or-later"

sources = [f"https://github.com/systemd/systemd/archive/refs/tags/v{pkgver}.tar.gz"]
depends = []

def build(c):
    c.SRCDIR = c.SRCDIR + f"/systemd-{pkgver}"
    c.env["CC"] = "gcc"
    c.env["CXX"] = "g++"

    #bullshitted args that work somehow 
    c.sh("meson", "setup", "build",
        "--prefix=/usr",
        "--buildtype=release",
        "-Dmode=release",
        "-Dlink-udev-shared=false",
        "-Dstandalone-binaries=true",
        "-Dbootloader=false",
        "-Dlogind=false",
        "-Dnetworkd=false",
        "-Dtimesyncd=false",
        "-Dmachined=false",
        "-Dimportd=false",
        "-Dhostnamed=false",
        "-Dtimedated=false",
        "-Dlocaled=false",
        "-Dcoredump=false",
        "-Dinitrd=false",
        "-Dhibernate=false",
        "-Dpam=false",
        "-Dselinux=false",
        "-Dpolkit=false",
        "-Dbacklight=false",
        "-Drfkill=false",
        "-Dpasswdqc=false",
        "-Dvconsole=false",
        "-Dquotacheck=false",
        "-Dldconfig=false",
        "-Dman=false"
        )
        
    c.sh("ninja", "-C", "build", f"-j{c.NPROC}")

def install(c):
    #big big ugly cleanu p
    c.env["DESTDIR"] = c.PKGDIR

    c.sh("ninja", "-C", "build", "install")
    c.sh("mkdir", "-p", "/tmp/udev-keep/usr/bin", "/tmp/udev-keep/usr/lib/pkgconfig", "/tmp/udev-keep/usr/include")

    c.sh("cp", "-a", c.PKGDIR + "/usr/bin/udevadm", "/tmp/udev-keep/usr/bin/", shell=True)
    c.sh("cp", "-a", c.PKGDIR + "/usr/lib/libudev.so*", "/tmp/udev-keep/usr/lib/", shell=True)
    c.sh("cp", "-a", c.PKGDIR + "/usr/include/libudev.h", "/tmp/udev-keep/usr/include/", shell=True)
    c.sh("cp", "-a", c.PKGDIR + "/usr/lib/pkgconfig/libudev.pc", "/tmp/udev-keep/usr/lib/pkgconfig", shell=True)

    if c.sh("test", "-d", c.PKGDIR + "/usr/lib/udev"):
        c.sh("cp", "-a", c.PKGDIR + "/usr/lib/udev", "/tmp/udev-keep/usr/lib/")
    if c.sh("test", "-d", c.PKGDIR + "/etc/udev"):
        c.sh("cp", "-a", c.PKGDIR + "/etc/udev", "/tmp/udev-keep/etc")

    c.sh("rm", "-rf", c.PKGDIR + "/*")

    c.sh("cp", "-a", "/tmp/udev-keep/*", c.PKGDIR + "/", shell=True)
    c.sh("rm", "-rf", "/tmp/udev-keep")
