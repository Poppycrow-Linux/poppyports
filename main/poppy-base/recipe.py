pkgname = "poppy-base"
pkgver = "0.0.1"
pkgrel = 0
pkgdesc = "Poppycrow base system package"
url = "https://www.poppycrow.org/"
arch = "x86_64"
license = "MIT"
sources = []

depends = [
  "linux-stable",
  "busybox",
  "glibc"
]

def build(c):
  pass

def install(c):
  c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init") # make init executable
  c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
