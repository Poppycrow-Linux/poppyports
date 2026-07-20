recipever = 0
pkgname = "busybox"
pkgver = "1.0.0"
pkgrel = 0
pkgdesc = "better gnu coreutils"
url = "https://www.busybox.net"
arch = "x86_64"
license = "GPL v2"

sources = ["git://busybox.net/busybox.git"]
depends = []


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}"
  c.sh("make", "defconfig")
  #sed -e 's/.*TC.*/CONFIG_TC=n/' -i .config
  c.sh("sed","-e","s/CONFIG_TC=y/CONFIG_TC=n/g","-i",".config") # disable tc to avoid bug TODO: FIX HACK HACK BUG
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make",f"CONFIG_PREFIX={c.PKGDIR}","install")
  #c.sh("cp", "./busybox", f"{c.PKGDIR}/bin")
  #c.sh("bash", "-c", f"mkdir {c.PKGDIR}/bin; cd bin; for i in $(./busybox --list); do ln -s ./busybox ./$i; done; cd ..")
