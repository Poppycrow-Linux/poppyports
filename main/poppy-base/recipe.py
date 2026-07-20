pkgname = "poppy-base"
pkgver = "0.0.1"
pkgrel = 0
pkgdesc = "Poppycrow base system package"
url = "https://www.poppycrow.org/"
arch = "x86_64"
license = "MIT"
sources = []

depends = [
  "main/linux-stable",
  "main/busybox",
  "main/glibc",
  "main/bash",
  "extra/nano",
  "extra/fastfetch",
  #"main/ncurses"
]

def build(c):
  pass

def install(c):
  c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init") # make init executable
  c.sh("mkdir","-p",f"{c.PORTDIR}/overlay/sys/fs/cgroup")
  c.sh("mkdir","-p",f"{c.PORTDIR}/overlay/dev/pts")
  c.sh("mkdir","-p",f"{c.PORTDIR}/overlay/dev/shm")
  c.sh("mkdir","-p",f"{c.PORTDIR}/overlay/proc")
  c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
