recipever = 0
pkgname = "fastfetch"
pkgver = "2.66.0"
pkgrel = 0
pkgdesc = "Fastfetch is a neofetch-like tool for fetching system information and displaying it in a visually appealing way."
url = "https://github.com/fastfetch-cli/fastfetch"
arch = "x86_64"
license = "MIT"

sbu = 0.9


sources = [f"{url}/archive/refs/tags/{pkgver}.tar.gz"]
sha256sum = ["547883c2f0dbc85a4545d4533f5b812fbc4c8ffe1271056de18b51994acbf474"]
depends = ['glibc', 'yyjson']
optdepends = ['libvulkan', 'libpulse', 'wayland', 'libdrm', 'libgio', 'dconf', 'libmagickcore', 'libchafa', 'zlib', 'dbus', 'libegl', 'libglx', 'libopencl', 'libxrandr', 'glib2', 'dconf', 'sqlite'] #TODO: complete the full list, package it, and also add a section to recipes that would allow to explain the fucntionality the packages provide a la arch linux. this section probably will be ignored by apk but handled by an apk wrapper i will start work on when we figure out how to add extra metadata to apks themselves.


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("cmake", f"{c.SRCDIR}")
  c.sh("cmake", "--build", f"{c.SRCDIR}", "--target", "fastfetch")
  #c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
