recipever = 0
pkgname = "linux-stable"
pkgver = "7.1.6"
pkgrel = 0
pkgdesc = "Linux Kernel (stable)"
url = "https://kernel.org/"
arch = ["x86_64","aarch64"]
license = "GPL v2"

sources = [f"https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-{pkgver}.tar.xz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/linux-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("make", "defconfig",f"ARCH={c.CROSS_KERNEL_ARCH}")
  if c.CROSS_KERNEL_ARCH == "x86":
    c.cp(f"{c.PORTDIR}/.config",f"{c.SRCDIR}/.config")
  c.sh("make",f"-j{c.NPROC}","LLVM=1",f"ARCH={c.CROSS_KERNEL_ARCH}")
  #c.sh("make","modules_install",f"-j{c.NPROC}")

def install(c):
  c.sh("mkdir", "-p", f"{c.PKGDIR}/boot")
  if c.CROSS_KERNEL_ARCH == "x86":
    c.sh("cp", f"{c.SRCDIR}/arch/{c.CROSS_KERNEL_ARCH}/boot/bzImage",f"{c.PKGDIR}/boot/bzImage")
  else:
    c.sh("cp", f"{c.SRCDIR}/arch/{c.CROSS_KERNEL_ARCH}/boot/Image",f"{c.PKGDIR}/boot/Image")
