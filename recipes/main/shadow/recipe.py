pkgname = "shadow"
pkgver = "4.18.0"
pkgrel = 0
pkgdesc = "Shadow password file utilities"
url = "https://github.com/shadow-maint/shadow"
arch = "all"
license = "BSD-3-Clause"

sources = [f"{url}/releases/download/{pkgver}/shadow-{pkgver}.tar.xz"]
depends = ["libc"]
makedepends = ["make"]


def build(c):
  configure_args = [
    "--enable-shared",
    "--enable-lastlog",
    "--disable-static",
    "--with-libpam",
    "--with-acl",
    "--with-attr",
    "--without-libbsd",
    "--without-selinux",
    "--without-nscd",
    "--prefix=/usr",
    "--without-group-name-max-length",
    "-sysconfdir=/etc",
    "--disable-nls",
    "--sysconfdir=/etc",
    "--enable-subordinate-ids",
    "--disable-account-tools-setuid",
  ]
  c.SRCDIR += f"/{pkgname}-{pkgver}"
  c.sh("./configure", *configure_args)
  c.sh("make", f"-j{c.NPROC}")

def install(c):
  filedir = f"{c.PORTDIR}/files"

  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")

  c.sh(f"rm -r {c.PKGDIR}/etc/pam.d/", shell = True)
  c.sh(f"mkdir -p {c.PKGDIR}/usr/etc/pam.d/")
  c.install_file(f"{filedir}/shadow-utils.pamd", f"{c.PKGDIR}/etc/pam.d/shadow-utils")
  for i in "groupmems", "chpasswd", "chfn", "newusers":
    c.lnk("shadow-utils", f"{c.PKGDIR}/etc/pam.d/{i}")
  c.install_file(f"{filedir}/chsh.pamd", f"{c.PKGDIR}/etc/pam.d/chsh", mode="644")
  c.install_file(f"/dev/null", f"{c.PKGDIR}/etc/subuid", mode = "644")
  c.install_file(f"/dev/null", f"{c.PKGDIR}/etc/subgid", mode = "644")
  c.sh(f"rm {c.PKGDIR}/etc/login.defs")
  c.install_file(f"{filedir}/login.defs", f"{c.PKGDIR}/etc/login.defs")

