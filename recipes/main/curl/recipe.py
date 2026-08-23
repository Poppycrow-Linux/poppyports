recipever = 0
pkgname = "curl"
pkgver = "8.21.0"
pkgrel = 0
pkgdesc = "URL retrieval utility and library"
url = "https://curl.se/"
arch = "all"
license = "curl"

depends = ["ca-certificates-bundle"]
makedepends = [
  "brotli-dev",
  "c-ares-dev",
  "groff",
  "libidn2-dev",
  "libpsl-dev",
  "nghttp2-dev",
  "openssl-dev",
  "perl",
  "python3",
  "zlib-dev",
  "zstd-dev",
]

sources = [f"https://curl.se/download/curl-{pkgver}.tar.xz"]


def build(c):
  c.SRCDIR = f"{c.SRCDIR}/{pkgname}-{pkgver}"

  c.sh("""./configure \
    --build="$CBUILD" \
    --host="$CHOST" \
    --prefix=/usr \
    --enable-ares \
    --enable-ipv6 \
    --enable-unix-sockets \
    --enable-static \
    --with-libidn2 \
    --with-nghttp2 \
    --with-openssl \
    --with-ca-bundle=/etc/ssl/certs/ca-certificates.crt \
    --with-ca-path=/etc/ssl/certs \
    --with-zsh-functions-dir \
    --with-fish-functions-dir \
    --disable-ldap \
    --with-pic \
    --enable-websockets \
    --without-libssh2
  """)

  c.sh("make")

  if not c.env.get("BOOTSTRAP"): #this is what alpine does. i know we don't even use the bootstrap var but i left the check in
    c.sh("make", "-C", "scripts")


def install(c):
  c.sh("make", "install", f"DESTDIR={c.PKGDIR}")

  if not c.env.get("BOOTSTRAP"): #this is what alpine does. i know we don't even use the bootstrap var but i left the check in
    c.install_file("scripts/_curl", f"{c.PKGDIR}/usr/share/zsh/site-functions/_curl", mode="644")
    c.install_file("scripts/curl.fish", f"{c.PKGDIR}/usr/share/fish/vendor_completions.d/curl.fish", mode="644")

  c.install_file("scripts/cd2nroff", f"{c.PKGDIR}/usr/bin/cd2nroff", mode="755")
