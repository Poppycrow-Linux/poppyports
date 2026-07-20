recipever = 0
pkgname = "busybox"
pkgver = "1.38.0"
pkgrel = 0
pkgdesc = "better gnu coreutils"
url = "https://www.busybox.net"
arch = "x86_64"
license = "GPL v2"

sources = ["https://busybox.net/downloads/busybox-1.38.0.tar.bz2"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/busybox-1.38.0"
  c.sh("make", "defconfig")
  #sed -e 's/.*TC.*/CONFIG_TC=n/' -i .config
  c.sh("sed","-e","s/CONFIG_TC=y/CONFIG_TC=n/g","-i",".config") # disable tc to avoid bug TODO: FIX HACK HACK BUG
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  #c.sh("make",f"CONFIG_PREFIX={c.PKGDIR}","install_flat")
  c.sh("mkdir","-p",f"{c.PKGDIR}/bin")
  c.sh("cp", "./busybox", f"{c.PKGDIR}/bin/busybox")
  c.sh("bash", "-c", f"mkdir -p {c.PKGDIR}/bin; cd {c.PKGDIR}/bin; for i in $(./busybox --list); do ln -s ./busybox ./$i; done; cd ..")
