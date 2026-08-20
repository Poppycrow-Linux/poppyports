pkgname = "gdbm"
pkgver = "1.26"
pkgrel = 2
pkgdesc = "GNU database library"
url = "https://www.gnu.org/software/gdbm/gdbm.html"
arch = "x86_64"
license = "GPL-3.0-or-later"

sources = [
    f"https://ftp.gnu.org/gnu/gdbm/gdbm-{pkgver}.tar.gz",
]
sha512sum = [
    "44aafe254f0950a8f5215d8f1337674f07b19f2a375f6eb19a7e39690028c80c3774b705c2b76b470ae74042b21f2ca77d02f6f57aa2ee50296db801220a3352",
]

depends = [
    "libc",
    "readline",
]


def build(c):
    c.SRCDIR += f"/gdbm-{pkgver}"

    c.sh(
        "./configure",
        "--prefix=/usr",
        "--enable-libgdbm-compat",
    )
    c.sh("make", f"-j{c.NPROC}")

    # Generate translation files.
    c.sh(
        "sh", "-c",
        "for po in po/*.po; do "
        'msgfmt "$po" -o "${po%.po}.mo"; '
        "done",
    )


def check(c):
    c.sh("make", "check", f"-j{c.NPROC}")


def install(c):
    c.sh("make", "install", f"DESTDIR={c.PKGDIR}")

    c.sh(
        "install", "-vDm644",
        "NOTE-WARNING",
        "AUTHORS",
        "NEWS",
        "README",
        "-t", f"{c.PKGDIR}/usr/share/doc/{pkgname}",
    )

    c.sh(
        "sh", "-c",
        "for mo in po/*.mo; do "
        f'mkdir -p "{c.PKGDIR}/usr/share/locale/${{mo##*/}}"; '
        "locale=${mo##*/}; "
        'locale=${locale%.mo}; '
        f'install -Dm644 "$mo" '
        f'"{c.PKGDIR}/usr/share/locale/$locale/LC_MESSAGES/{pkgname}.mo"; '
        "done",
    )
