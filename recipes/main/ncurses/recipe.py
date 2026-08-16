recipever = 0
pkgname = "ncurses"
pkgver = "6.6"
pkgrel = 0
pkgdesc = "Free software emulation of curses in System V Release 4.0 (SVr4), and more."
url = "https://invisible-island.net/ncurses/"
arch = "x86_64"
license = "MIT/X11"
maintainer = "cachewave"

sbu = 1.0

sources = [f"https://ftp.gnu.org/gnu/ncurses/{pkgname}-{pkgver}.tar.gz"]
sha256sum = ["355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11"]
depends = ["libc"]

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("./configure","--enable-widec","--with-shared","--without-normal","--without-debug","--with-termlib", "--with-cxx-shared", "--with-cxx-binding", "--enable-pc-files", "--disable-stripping", "--enable-symlinks", "--with-versioned-syms")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}", f"-j{c.NPROC}") # should be also symlinked to /lib64
  print("Time for symlink jank! if anything errors out, nuke the ncurses build directory!")
  oldsrcdir = c.SRCDIR
  c.SRCDIR = c.PKGDIR + "/usr/lib" # hack because sh doesnt allow to set cwd
  #c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so.6")
  #c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so")
  #c.sh("ln","-s","libtinfow.so.6.6","libtinfo.so.6.6")

  c.SRCDIR=c.PKGDIR #SET IT BACK
  ## they taught me this ncurses trick at the alpine linux APKBUILDS school
  for lib in ["ncurses", "ncurses++", "form", "panel", "menu"]:
    c.sh(f"ln -s {lib}w.pc {c.PKGDIR}/usr/lib/pkgconfig/{lib}.pc")
    c.sh(f"ln -s lib{lib}w.a {c.PKGDIR}/usr/lib/lib{lib}.a")
    c.sh(f"ln -s lib{lib}w.so {c.PKGDIR}/usr/lib/lib{lib}.so")

  # and one more for the fans!

  for lib in ["curses", "tic", "tinfo"]:
    c.sh(f"ln -s libncurses.a {c.PKGDIR}/usr/lib/lib{lib}.a")
    c.sh(f"ln -s libncurses.so {c.PKGDIR}/usr/lib/lib{lib}.so")
    c.sh(f"ln -s ncurses.pc {c.PKGDIR}/usr/lib/pkgconfig/{lib}.pc")

  c.sh(f"ln -s libncursesw.so {c.PKGDIR}/usr/lib/libcursesw.so")
