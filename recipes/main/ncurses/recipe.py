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
build_style = "gnu_configure"
build_wrksrc = f"{pkgname}-{pkgver}"
make_check = False

configure_args = [
    "--enable-widec",
    "--with-shared",
    "--with-manpage-symlinks",
    "--with-manpage-format=normal",
    "--without-debug",
    "--with-termlib",
    "--with-cxx-shared",
    "--with-cxx-binding",
    "--enable-pc-files",
    "--disable-stripping",
    "--enable-symlinks",
    "--with-pkg-config-libdir=/usr/lib/pkgconfig",
    "--with-versioned-syms",
]


def install(c):
    c.sh(
        "make",
        "install",
        f"DESTDIR={c.PKGDIR}",
        f"-j{c.NPROC}",
        cwd=c.workdir(),
    )

    # Symlink jank
    libdir = f"{c.PKGDIR}/usr/lib"
    pkgconfig_dir = f"{libdir}/pkgconfig"
    for lib in ["ncurses", "ncurses++", "form", "panel", "menu"]:
      c.lnk(f"{pkgconfig_dir}/{lib}w.pc", f"{pkgconfig_dir}/{lib}.pc", relative=True)
      c.lnk(f"{libdir}/lib{lib}w.a", f"{libdir}/lib{lib}.a", relative=True)
      c.lnk(f"{libdir}/lib{lib}w.so", f"{libdir}/lib{lib}.so", relative=True)

    for lib in ["curses", "tic", "tinfo"]:
      c.lnk(f"{libdir}/libncurses.a", f"{libdir}/lib{lib}.a", relative=True)
      c.lnk(f"{libdir}/libncurses.so", f"{libdir}/lib{lib}.so", relative=True)
      c.lnk(f"{pkgconfig_dir}/ncurses.pc", f"{pkgconfig_dir}/{lib}.pc", relative=True)

    c.lnk(f"{libdir}/libncursesw.so", f"{libdir}/libcursesw.so", relative=True)
