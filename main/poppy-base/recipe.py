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
  "glibc",
  "bash",
  "apk-tools",
  # below is not base but i'm keeping it in for now. TODO: make a new system-base package this sucks
  "fastfetch",
  "bsdgames",
  "figlet",
  # this is BAD syntax and will not work!!
  #"editors/nano",
  #"main/wayland",
  #"xorg/xorg-xserver",
  #"main/libinput",
  #"main/dinit",
  #"main/libffi",
  #"main/libdrm",
  #"main/libxkbcommon"
]

def build(c):
  pass

def install(c):
  c.sh("chmod", "+x", f"{c.PORTDIR}/overlay/init") # make init executable
  c.cp(f"{c.PORTDIR}/overlay/.", c.PKGDIR)
