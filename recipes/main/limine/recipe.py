recipever = 0
pkgname = "limine"
pkgver = "12.6.0"
pkgrel = 0
pkgdesc = "Limine is a modern, secure, portable, multiprotocol bootloader and boot manager, also used as the reference implementation for the Limine boot protocol."
url = "https://github.com/limine-bootloader/limine"
arch = "x86_64"
license = "BSD-2-Clause license"


sources = [f"{url}/releases/download/v{pkgver}/{pkgname}-{pkgver}.tar.gz"]
depends = []
makedepends = ['make', 'grep', 'sed', 'find', 'awk', 'nasm', 'mtools'] # techincally clang or gcc is also needed but idk about it



def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh(f"{c.SRCDIR}/bootstrap")
  if c.ARCH == "x86_64":
      c.sh(f"{c.SRCDIR}/configure --enable-bios --enable-bios-cd --enable-uefi-x86-64 --enable-uefi-cd") #TODO: maybe split the cd things into its own package?
  c.sh("make")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}") # bash adds its own /usr for some reason
