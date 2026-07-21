recipever = 0
pkgname = "libxkbcommon"
pkgver = "1.13.2"
pkgrel = 0
pkgdesc = "libxkbcommon is a keyboard keymap compiler"
url = "https://xkbcommon.org/"
arch = "x86_64"
license = "MIT"

sources = [f"https://github.com/xkbcommon/libxkbcommon/archive/refs/tags/xkbcommon-1.13.2.tar.gz"]
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/libxkbcommon-xkbcommon-1.13.2" # TODO fix this is because tar files have a top level name
  #c.sh("meson","setup","build","-Denable-x11=false",f"-Dprefix={c.PKGDIR}",f"-Dxkb-config-root={c.PKGDIR}/usr/share/xkeyboard-config-2",f"-Dxkb-legacy-root={c.PKGDIR}/usr/share/X11/xkb",f"-Dxkb-config-unversioned-extensions-path={c.PKGDIR}/usr/share/xkeyboard-config.d",f"-Dxkb-config-versioned-extensions-path={c.PKGDIR}/usr/share/xkeyboard-config-2.d")
  c.sh("meson","setup","build","-Denable-x11=false",f"-Dprefix={c.PKGDIR}",f"-Dxkb-config-root={c.PKGDIR}/usr/share/xkeyboard-config-2",f"-Dxkb-config-unversioned-extensions-path={c.PKGDIR}/usr/share/xkeyboard-config.d",f"-Dxkb-config-versioned-extensions-path={c.PKGDIR}/usr/share/xkeyboard-config-2.d","-Denable-bash-completion=false")
  c.sh("meson","compile","-C","build")

def install(c):
  c.sh("meson","install","-C","build")
  print("idk")
