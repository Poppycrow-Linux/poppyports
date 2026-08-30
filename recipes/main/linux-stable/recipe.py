# this is the linux-stable recipe, which also serves as an example on how to package a generic Linux
pkgname = "linux-stable"
pkgver = "7.2.2"
pkgrel = 0
pkgdesc = "The Linux kernel (stable)"
url = "https://www.kernel.org/"
arch = ["x86_64", "aarch64", "armv7", "i686", "riscv64", "ppc64le", "s390x"]
license = "GPL-2.0-only"

sources = [f"https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-{pkgver}.tar.xz"]

depends = ["libc", "linux-headers"]
makedepends = ["bc", "bison", "flex", "make", "openssl", "perl"]

build_style = "kernel"
build_wrksrc = f"linux-{pkgver}"

kernel_config = ".config" # looks for a config in {c.PORTDIR}/{kernel_config}
kernel_defconfig = "defconfig" # this is what kind of make target runs if the config is not present
kernel_make_args = [] # if you guess what this does i am going to kill myself
kernel_make_targets = [""] # what make target is called on build. we leave it empty because make already produces a kernel.
kernel_install_image = True # puts the bzimage into /boot, true by default
kernel_install_modules = True # whether or not to include modules in the package

make_check = False # runs the kernel self-test
