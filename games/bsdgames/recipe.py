recipever = 0
pkgname = "bsdgames"
pkgver = "3.2.0"
pkgrel = 0
pkgdesc = "BSD Games"
url = "https://github.com/thesamesam/bsd-games"
arch = "x86_64"
license = "BSD"

sources = [f"https://github.com/thesamesam/bsd-games/archive/refs/tags/v3.2.tar.gz"]
depends = ["ncurses"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/bsd-games-3.2" # TODO fix this is because tar files have a top level name
  c.sh("patch", "-p1", "-i", c.PORTDIR + "/fixup.patch")
  c.sh("patch", "-p1", "-i", c.PORTDIR + "/ncurseswhack.patch")
  c.sh("./configure",f"--prefix={c.PKGDIR}/usr",f"--localstatedir={c.PKGDIR}/var/lib")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install")
