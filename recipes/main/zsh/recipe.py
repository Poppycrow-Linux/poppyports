recipever = 0
pkgname = "zsh"
pkgver = "5.9.2"
pkgrel = 0
pkgdesc = "A very advanced and programmable command interpreter (shell) for UNIX."
url = "https://www.zsh.org/"
arch = "x86_64"
license = "Custom"


sources = [f"{url}pub/zsh-{pkgver}.tar.xz"]
depends = ["libc", "libcap", "pcre2"]
makedepends = ['gdbm', 'yodl']

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}"
  c.sh("./configure \
    --prefix=/usr \
    --docdir=/usr/share/doc/zsh \
    --htmldir=/usr/share/doc/zsh/html \
    --enable-etcdir=/etc/zsh \
    --enable-zshenv=/etc/zsh/zshenv \
    --enable-zlogin=/etc/zsh/zlogin \
    --enable-zlogout=/etc/zsh/zlogout \
    --enable-zprofile=/etc/zsh/zprofile \
    --enable-zshrc=/etc/zsh/zshrc \
    --enable-maildir-support \
    --with-term-lib='ncursesw' \
    --enable-multibyte \
    --enable-function-subdirs \
    --enable-fndir=/usr/share/zsh/functions \
    --enable-scriptdir=/usr/share/zsh/scripts \
    --with-tcsetpgrp \
    --enable-pcre \
    --enable-gdbm \
    --enable-cap \
    --enable-zsh-secure-free")
  c.sh(f"make -j{c.NPROC}")

def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}", f"-j{c.NPROC}")
  c.lnk(f"{c.PKGDIR}/usr/bin/zsh", f"{c.PKGDIR}/usr/bin/sh", relative = True)
  # todo: also package license
