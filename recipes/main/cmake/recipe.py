pkgname = "cmake"
pkgver = "4.4.2"
pkgrel = 0
pkgdesc = "CMake Utility"
url = "https://cmake.org/"
arch = "x86_64"
license = "BSD-3-Clause"

build_wrksrc = f"{pkgname}-{pkgver}"
sources = [f"https://github.com/Kitware/CMake/releases/download/v4.4.2/{pkgname}-{pkgver}.tar.gz"]
depends = ["libc", "openssl", "libarchive", "curl", "libexpat", "ncurses", "rhash", "llvm", "libuv", "zlib"]
# libunwind is llvm
makedepends = ["make"]
hostmakedepends = ["cmake", "linux-headers", "libarchive"]
build_style = "cmake"
make_check = False

#configure_args = [
  #"-DCMAKE_MAN_DIR=/share/man",
  #"-DCMAKE_DOC_DIR=/share/doc/cmake",
  #"-DCMAKE_USE_SYSTEM_LIBARCHIVE=ON",
  #"-DCMAKE_USE_SYSTEM_ZLIB=ON",
  #"-DCMAKE_USE_SYSTEM_BZIP2=ON",
  #"-DCMAKE_USE_SYSTEM_LIBLZMA=ON",
  #"-DCMAKE_USE_SYSTEM_ZSTD=ON",
  #"-DCMAKE_USE_SYSTEM_CURL=ON",
  #"-DCMAKE_USE_SYSTEM_NGHTTP2=ON",
  #"-DCMAKE_USE_SYSTEM_EXPAT=ON",
  #"-DCMAKE_USE_SYSTEM_LIBUV=ON",
  #"-DCMAKE_USE_SYSTEM_LIBRHASH=ON"
#]

configure_args = [
  "-DCMAKE_MAN_DIR=/share/man",
  "-DCMAKE_DOC_DIR=/share/doc/cmake"
]
