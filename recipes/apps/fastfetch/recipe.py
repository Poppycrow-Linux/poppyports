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
depends = ['glibc']


def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh("cmake", f"{c.SRCDIR}")
  c.sh("cmake", "--build", f"{c.SRCDIR}", "--target", "fastfetch")
  #c.sh("make", f"MYCFLAGS={c.CFLAGS}", f"MYLDFLAGS={c.LDFLAGS}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
