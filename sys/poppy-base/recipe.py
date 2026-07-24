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
  "main/ncurses",
  "main/zlib",
  "main/wayland",
  "main/apk",
  "main/openssl"
  "main/x11-server",

  "extra/bsdgames",
  "extra/figlet",
  "main/libinput",
  "main/dinit",
  "main/libffi",
  "main/libdrm",
  "main/libxkbcommon"
]

def build(c):
  pass

def install(c):
  c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init") # make init executable
