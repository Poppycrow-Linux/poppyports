recipever = 0
pkgname = "libinput"
pkgver = "1.31.3"
pkgrel = 0
pkgdesc = "libinput is a library that provides a full input stack for display servers \
and other applications that need to handle input devices provided by the \
kernel."
url = "https://wayland.freedesktop.org/libinput/doc/latest/"
arch = "x86_64"
license = "MIT"


sources = [f"https://gitlab.com/freedesktop-sdk/mirrors/freedesktop/libinput/libinput/-/archive/{pkgver}/{pkgname}-{pkgver}.tar.gz?ref_type=tags"]
sha256sum = ["b6749bf6f1890f6631c0a70a027c35fec9d2e096a39f720548896e41474a9854"]
depends = []


def build(c):
  
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("meson","setup",f"--prefix={c.PKGDIR}/usr", f"build/")
  c.sh("ninja", "-C", f"build/")

def install(c):
  c.sh("ninja", "-C", f"build/", "install")
