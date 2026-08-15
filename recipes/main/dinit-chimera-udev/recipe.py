# cachewave this notice is for YOU
# you looove consolidating packages and services but this would not make sense here since
# it has standalone executables and scripts, which makes it good enough to consider a separate program
# right now i am doing random stuff to try and make dinit (primarily dinit-poppy because most dinit services are written with it in mind) work
# - valeradxdinit.


# okay so new findings
# apperently what I packaged as tiny-devd is supposed to come with this package. and the edit i made for it is actually STUPID
# because dinit-chimera comes with their udev wrapper that's NOT a symlink or a copy of udevadm
# i know that everyone will read this in a single sitting and whatnot but I will leave those comments here regardless

# TODO: remove the tiny devd package once this one works.
# - valeradx NOTDINIT

# more findings: udevd IS a symlink to udevd i am just an idiot
# - valeradudev=true

recipever = 0
pkgname = "dinit-chimera-udev" # making a fork wouldn't really make sense since idk what there is to improve
pkgver = "0.1.0"
pkgrel = 0
pkgdesc = "Udev integration for dinit that allows to depend on specific devices"
url = "https://github.com/chimera-linux/dinit-chimera-udev"
arch = "x86_64"
license = "BSD-2-Clause"

sources = [f"{url}/archive/v{pkgver}.tar.gz"]
sha256 = ["346a4012b9d6364b243d8191123bdbdfae9c445c3e40abd0c225a1009f650eeb"]

depends = ["dinit", "libdinitctl"]
makedepends = ["meson"]


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  global bdir
  bdir = c.SRCDIR + "/build"
  c.sh("meson setup --reconfigure --wipe build/")
  c.sh("meson compile", cwd = bdir)

  # i feel like this should be something else?
  # it's not really a part of installation process and moreso prep work but doesn't fit into prepare chronologically either
  c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib")
  c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib/dinit.d")
  c.sh("mkdir", "-p", f"{c.PKGDIR}/usr/lib/dinit.d/early")

def install(c):
  c.sh(f"mkdir -p {c.PKGDIR}/usr/lib/dinit.d/early/helpers")
  c.sh(f"mkdir -p {c.PKGDIR}/usr/lib/dinit.d/boot.d")
  c.sh(f"mkdir -p {c.PKGDIR}/usr/libexec/")

  for i in "devmon", "devclient":
      c.cp(f"{bdir}/helpers/{i}", f"{c.PKGDIR}/usr/lib/dinit.d/early/helpers/{i}")
      c.sh(f"chmod +x {c.PKGDIR}/usr/lib/dinit.d/early/helpers/{i}")
      c.cp(f"{c.PORTDIR}/files/udevd.wrapper", f"{c.PKGDIR}/usr/lib/udevd.wrapper")
      c.sh(f"chmod +x {c.PKGDIR}/usr/lib/udevd.wrapper")
      c.cp(f"{c.PORTDIR}/files/dinit-devd", f"{c.PKGDIR}/usr/lib/dinit-devd")
      c.cp(f"{c.PORTDIR}/files/dinit-devd", f"{c.PKGDIR}/usr/libexec/dinit-devd")
      c.sh(f"chmod +x {c.PKGDIR}/usr/lib/dinit-devd")
      c.sh(f"chmod +x {c.PKGDIR}/usr/libexec/dinit-devd")
      c.cp(f"{c.PORTDIR}/files/udevd", f"{c.PKGDIR}/usr/lib/dinit.d/udevd")
