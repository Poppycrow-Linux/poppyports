recipever = 0
pkgname = "wlmaker"
pkgver = "0.8.1"
pkgrel = 0
pkgdesc = "A Wayland compositor that replicates the look and the behavior of WindowMaker"
url = "https://github.com/phkaeser/wlmaker"
arch = "x86_64"
license = "Apache-2.0"
# https://github.com/phkaeser/wlmaker/releases/download/v0.8.1/wlmaker-0.8.1.tar.gz
sources = [f"{url}/releases/download/v{pkgver}/{pkgname}-{pkgver}.tar.gz"]

depends = ['bison', 'flex', 'git', 'libcairo2-dev', 'libncurses-dev', 'libwlroots-0.18-dev', 'pkg-config', 'plantuml', 'xwayland']
makedepends = ['gcc', 'cmake', 'doxygen', 'wayland-protocols', 'git', 'clang']

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-{pkgver}" # TODO fix this is because tar files have a top level name
  c.sh('ls')
  c.sh(f'git submodule update --init {c.SRCDIR}/submodules/', shell = True, cwd = c.SRCDIR)
  c.sh(f'cmake -DCMAKE_INSTALL_PREFIX="{c.PKGDIR}" -B build/')
  c.sh('make', cwd = c.SRCDIR + "/build")


def install(c):
  c.sh(f'make DESTDIR={c.PKGDIR} install', cwd = c.SRCDIR + "/build")
