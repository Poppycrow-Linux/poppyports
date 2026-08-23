recipever = 0
pkgname = "linux-pam-base"
pkgver = "0"
pkgrel = 0

pkgdesc = "Pluggable Authentication Modules for Linux (config files)"
url = "https://github.com/linux-pam/linux-pam"
arch = "x86_64"
license = "None"

sources = []
depends = ["linux-pam"]


def build(c):
  pass


def install(c):
  import os
  c.sh(f"mkdir -p {c.PKGDIR}usr/lib/pam.d")
  for f in os.listdir(f"{c.PORTDIR}/files"):
    c.install_file(f"{c.PORTDIR}/files/{f}",f"{c.PKGDIR}/usr/lib/pam.d", mode=0o644)

