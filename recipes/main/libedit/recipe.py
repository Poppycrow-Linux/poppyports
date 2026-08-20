## use this instead of readline whenever possible. I should update my zsh recipe to use libedit as opposed to readline.
# we will package both and probably won't patch apps to support it but if there is an option to use it instead of readline, use it.
recipever = 0
pkgname = "libedit"
pkgver = "20250614"
pkgrel = 0

_gitrev = "b280b361724a60fa8b740150950a59c4f4edcf15"

pkgdesc = "Port of the NetBSD command line editing library"
url = "https://github.com/chimera-linux/libedit-chimera"
arch = "x86_64"
license = "BSD-3-Clause"

sources = [f"{url}/archive/{_gitrev}.tar.gz"]
sha256 = "aa0fcba24403e002b3f7f6e9cf41616d8f637ce5a5708a36450f1127887f412c"

depends = ["libc", "ncurses"]
makedepends = ["ncurses-devel", "pkgconf"]


def build(c):
    c.SRCDIR = c.SRCDIR + f"/libedit-chimera-{_gitrev}"
    c.sh(f"patch -p1 < {c.PORTDIR}/patches/glibc.patch")
    c.sh("make")


def install(c):
    incdir = f"{c.PKGDIR}/usr/include/readline"
    libdir = f"{c.PKGDIR}/usr/lib"

    c.sh("make", f"DESTDIR={c.PKGDIR}","PREFIX=/usr","install",)

    c.sh("mkdir", "-p", incdir, libdir)

    ## those are a nuclear option for when we want to replace readline with libedit but i commented it out since we can and do provide
    # both
    """
    for header in ("readline.h", "history.h"):
        c.cp(
            f"{c.PORTDIR}/files/{header}",
            f"{incdir}/{header}",
        )

    for library in ("libhistory.so", "libreadline.so"):
        c.cp(
            f"{c.PORTDIR}/files/{library}",
            f"{libdir}/{library}",
        )


    c.lnk("libedit.a", f"{libdir}/libreadline.a", relative=True)
    c.lnk("libedit.a", f"{libdir}/libhistory.a", relative=True)
    """

    c.lnk("libedit.pc", f"{libdir}/pkgconfig/readline.pc", relative=True)
