recipever = 0
pkgname = "muon"
pkgver = "0.6.0"
pkgrel = 0
pkgdesc = "C99 implementation of the Meson build system"
url = "https://muon.build/"
arch = "x86_64"
license = "GPLv3"

sources = [f"https://muon.build/releases/v{pkgver}/{pkgname}-v{pkgver}.tar.gz"] # i dont think this is getting updated anytime soon
depends = ['libc', 'ninja']
optdepends = ['pkg-config', 'curl', 'libarchive', 'scdoc', 'python-pyaml', 'python'] #todo: package curl and libcurl. and also make libcurl a subpackage.

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-v{pkgver}" # TODO fix this is because tar files

  #hack hack patch
  c.sh(f"patch -t -Np1 -i {c.PORTDIR}/patches/pkgconf3.patch") # this patch won't be needed once muon 0.7.0 is released

  #stage 1: bootstrap
  c.sh("./bootstrap.sh build-stage1")

  print("stage 2: muon from bootstrap")
  #ok so we disable samurai (which is like ninja but c99) because we do have proper ninja but should we package it separately or something? thoughts?
  c.sh('build-stage1/muon-bootstrap setup \
    -D libarchive=disabled \
    -D libcurl=disabled \
    -D libpkgconf=enabled \
    -D man-pages=disabled \
    -D meson-docs=disabled \
    -D meson-tests=disabled \
    -D readline=builtin \
    -D samurai=enabled \
    -D static=false \
    -D tracy=disabled \
    -D ui=disabled \
    -D website=disabled \
    build-stage2')
  c.sh("ninja -C build-stage2")

  print("FINAL STAGE: muon from muon")
  #we also disable samurai here too
  c.sh("build-stage2/muon setup \
    -D libarchive=enabled \
    -D libcurl=enabled \
    -D libpkgconf=enabled \
    -D man-pages=enabled \
    -D meson-docs=disabled \
    -D readline=builtin \
    -D samurai=disabled \
    -D static=false \
    -D tracy=disabled \
    -D ui=disabled \
    -D website=disabled \
    -D prefix=/usr \
    -D b_lto=true \
    -D b_pie=true \
    build")
  c.sh("ninja -C build")

def install(c):
  c.sh(f"DESTDIR={c.PKGDIR} build/muon -C build install")
