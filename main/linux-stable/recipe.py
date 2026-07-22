recipever = 0
pkgname = "linux-stable"
pkgver = "7.1.4"
pkgrel = 0
pkgdesc = "Linux Kernel (stable)"
url = "https://kernel.org/"
arch = "x86_64"
license = "GPL v2"

sources = [f"https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-7.1.4.tar.xz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + "/linux-7.1.4" # TODO fix this is because tar files have a top level name
  c.sh("make", "defconfig")
  c.cp(f"{c.PORTDIR}/.config",f"{c.SRCDIR}/.config")
  c.sh("make",f"-j{c.NPROC}","LLVM=1")
  #c.sh("make","modules_install",f"-j{c.NPROC}")

def install(c):
  c.sh("mkdir", "-p", f"{c.PKGDIR}/boot")
  c.sh("cp", f"{c.SRCDIR}/arch/x86/boot/bzImage",f"{c.PKGDIR}/boot/bzImage")
