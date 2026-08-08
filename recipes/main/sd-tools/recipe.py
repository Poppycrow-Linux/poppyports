recipever = 0
pkgname = "sd-tools"
pkgver = "0.99.0"
pkgrel = 0
pkgdesc = "A collection of tools forked from systemd (tmpfiles and sysusers)"
url = "https://github.com/chimera-linux/sd-tools"
arch = "x86_64"
license = "LGPL 2.1"

#sources = [f"{url}/archive/refs/tags/v{pkgver}.tar.gz"]
sources = ["https://github.com/chimera-linux/sd-tools/archive/refs/heads/master.tar.gz"] # master will do for now
depends = []

def build(c):
  c.SRCDIR = c.SRCDIR + f"/{pkgname}-master" # TODO fix this is because tar files have a top level name
  c.sh("meson","build/")
  c.sh("ninja","all", cwd = f"{c.SRCDIR}/build")

# hastag fast
def install(c):
  for i in ["sysusers", "tmpfiles"]:
    c.sh(f"mkdir -p {c.PKGDIR}/usr/bin")
    c.cp(f"{c.SRCDIR}/build/src/{i}/sd-{i}",f"{c.PKGDIR}/usr/bin/")
    c.sh(f"chmod +x {c.PKGDIR}/usr/bin/sd-{i}")
    c.lnk(f"{c.PKGDIR}/usr/bin/systemd-{i}", f"{c.PKGDIR}/usr/bin/{i}") # supposedly deprecated but okay
