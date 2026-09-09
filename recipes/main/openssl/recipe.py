pkgname = "openssl"
pkgver = "3.5.7"
pkgrel = 0
pkgdesc = "Library for various kinds of cryptography"
url = "openssl-library.org"
arch = ["x86_64", "aarch64"]
license = "Apache-2.0"

sources = [f"https://github.com/openssl/openssl/releases/download/openssl-{pkgver}/openssl-{pkgver}.tar.gz"]
depends = ["libc"]
hostmakedepends = ["pkgconf", "perl"]
build_style = "gnu_configure"
configure_command = "Configure"
build_wrksrc = f"{pkgname}-{pkgver}"
configure_args = ["--prefix=/usr", "shared", "--openssldir=/etc/ssl"]

add_cross_params = False
make_check = False

def prepare(c):
  global configure_args
  c.env["CROSS_COMPILE"] = "" # needed because openssl treats it as a prefix. the fuck???
  if c.ARCH == "x86_64":
    configure_args += ["enable-ec_nistp_64_gcc_128", "linux-x86_64"]
  elif c.ARCH in ("aarch64", "ppc64le", "ppc64", "ppc"):
    configure_args += [f"linux-{c.ARCH}"]
  elif c.ARCH in ("riscv64", "loongarch64"):
    configure_args += [f"linux64-{c.ARCH}"]
  elif c.ARCH in ("armhf", "armv7"):
    configure_args += ["linux-armv4"] # who the fuck calls armv7 armv4 lmao
  else:
    raise RuntimeError(f"Unknown CPU architecture: {c.ARCH}")
  configure_args += c.CFLAGS.split()
  configure_args += c.LDFLAGS.split()
