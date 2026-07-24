recipever = 0
pkgname = "limine"
pkgfoldername = "Limine"
pkgver = "12.5.2"
pkgrel = 0
pkgdesc = "Limine is a modern, secure, portable, multiprotocol bootloader and boot manager, also used as the reference implementation for the Limine boot protocol."
url = "https://github.com/limine-bootloader/limine"
arch = "x86_64"
license = "MIT"


sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
depends = []



def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgfoldername}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(f"{c.SRCDIR}/bootstrap")
  c.sh(f"{c.SRCDIR}/configure", "--help")
  c.sh("make") # cwd=c.SRCDIR argument is implied

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
