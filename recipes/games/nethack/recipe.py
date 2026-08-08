recipever = 0
pkgname = "nethack"
pkgver = "5.0.0"
pkgrel = 0
pkgdesc = "An open source fork of the adventure game Rogue--a turn based, tile based roguelike"
url = "nethack.org"
arch = "x86_64"
license = "NetHack License"

sources = [f"https://www.nethack.org/download/5.0.0/nethack-500-src.tgz"] #Yes, you really have to hardcode this--because they tag versions like this
depends = ["ncurses"] 

def build(c):
  c.SRCDIR = c.SRCDIR + f"/NetHack-5.0.0" 
  c.sh("./sys/unix/setup.sh", f"./sys/unix/hints/linux.500")
 # c.sh("./configure",f"--prefix={c.PKGDIR}/usr",f"--localstatedir={c.PKGDIR}/var/lib")
  c.sh("make", "fetch-lua")
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"PREFIX={c.PKGDIR}/var")
