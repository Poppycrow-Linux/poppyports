#!/bin/bash
# builds a pinned bootstrap toolchain for compiling a linux glibc system
# tested with debian trixie/forky
# adapted from LFS book: https://www.linuxfromscratch.org/lfs/view/systemd/partintro/introduction.html
# WORK IN PROGRESS! Remove this comment once working
set -euo pipefail

TARGET="${TARGET:-x86_64-crow-linux-gnu}"
PREFIX="${PREFIX:-$PWD/build/ccstrap}"

BINUTILS_VERSION="2.47"
GCC_VERSION="16.2.0"
GLIBC_VERSION="2.44"
HEADERS_VERSION="7.1.8"



SYSROOT="$PREFIX/sysroot"
SOURCES="$PREFIX/srcs"
BUILD="$PREFIX/build"
mkdir -p "$PREFIX" "$SYSROOT" "$SOURCES" "$BUILD"

echo "sysroot: $SYSROOT | sources: $SOURCES | build: $BUILD"


testcmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "command missing: $1"
    exit 1
  }
}

for cmd in bash gcc g++ make bison flex python3 wget tar xz bzip2 gzip patch ldconfig; do
  testcmd "$cmd"
done


export PATH="$SYSROOT/bin:$SYSROOT/tools/bin:$PATH"
export MAKEFLAGS="-j$(nproc)"

download() {
  if [[ -f "$2" ]]; then
    echo "I: already downloaded $2"
    return
  fi
  wget --output-document="$2" "$1"
}

extract() {
  if [[ -d "$2" ]]; then
    echo "I: already extracted $2"
    return
  fi
  echo "I: extracting $1"
  mkdir -p "$2"
  tar -xf "$1" -C "$2" --strip-components=1
}

# download and extract toolchain
download "https://ftp.gnu.org/gnu/binutils/binutils-${BINUTILS_VERSION}.tar.xz" "$SOURCES/binutils.tar.xz"
download "https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.xz" "$SOURCES/gcc.tar.xz"
download "https://ftp.gnu.org/gnu/glibc/glibc-${GLIBC_VERSION}.tar.xz" "$SOURCES/glibc.tar.xz"
download "https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-${HEADERS_VERSION}.tar.xz" "$SOURCES/linux.tar.xz"

extract "$SOURCES/binutils.tar.xz" "$SOURCES/binutils"
extract "$SOURCES/gcc.tar.xz" "$SOURCES/gcc"
extract "$SOURCES/glibc.tar.xz" "$SOURCES/glibc"
extract "$SOURCES/linux.tar.xz" "$SOURCES/linux"


# --------- STAGE 1 BUILDING
# binutils
BUILDDIR="$BUILD/binutils"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

"$SOURCES/binutils/configure" \
  --target="$TARGET" --prefix="$SYSROOT/tools" --with-sysroot="$SYSROOT" \
  --disable-nls --enable-gprofng=no --disable-werror \
  --enable-new-dtags

make
make install


# gcc
cd "$SOURCES/gcc"
./contrib/download_prerequisites --no-verify

BUILDDIR="$BUILD/gcc"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

"$SOURCES/gcc/configure" \
  --target="$TARGET" --prefix="$SYSROOT/tools" --with-sysroot="$SYSROOT" \
  --with-glibc-version=$GLIBC_VERSION \
  --with-newlib --without-headers \
  --enable-default-pie --enable-default-ssp \
  --disable-fixincludes \
  --disable-nls \
  --disable-shared \
  --disable-multilib \
  --disable-threads \
  --disable-libatomic --disable-libgomp --disable-libquadmath \
  --disable-libssp --disable-libvtv --disable-libstdcxx \
  --enable-languages=c,c++

make
make install

# kernel headers
cd "$SOURCES/linux"
make mrproper
make headers
find usr/include -type f ! -name '*.h' -delete
mkdir -p "$SYSROOT/usr/"
cp -rv usr/include "$SYSROOT/usr/"


# glibc
BUILDDIR="$BUILD/glibc"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

GUESS="$($SOURCES/glibc/scripts/config.guess)"
"$SOURCES/glibc/configure" \
  --prefix=/usr --host="$TARGET" --build="$GUESS" \
  --disable-nscd \
  libc_cv_slibdir=/usr/lib \
  --enable-kernel=5.10

make
make DESTDIR="$SYSROOT" install

sed '/RTLDLIST=/s@/usr@@g' -i $SYSROOT/usr/bin/ldd

# TODO: tests from https://www.linuxfromscratch.org/lfs/view/systemd/chapter05/glibc.html


# libstdc++ from gcc
# https://www.linuxfromscratch.org/lfs/view/systemd/chapter05/gcc-libstdc++.html
BUILDDIR="$BUILD/libstdc++"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

"$SOURCES/gcc/libstdc++-v3/configure" \
  --prefix=/usr --host="$TARGET" --build="$GUESS" \
  CXX=$TARGET-gcc \
  --disable-multilib \
  --disable-nls \
  --disable-libstdcxx-pth \
  --with-gxx-include-dir=/tools/$TARGET/include/c++/16.2.0

make
make DESTDIR="$SYSROOT" install

rm -v $SYSROOT/usr/lib/lib{stdc++{,exp,fs},supc++}.la



# --------- STAGE 2 BUILDING
# we can (hopefully) skip the arch independent crap here, such as M4 ncurses file make... because they shouldn't cause big problems
# binutils
BUILDDIR="$BUILD/binutils2"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

sed '6031s/$add_dir//' -i $SOURCES/binutils/ltmain.sh

"$SOURCES/binutils/configure" \
  --prefix=/usr --build="$GUESS" --host="$TARGET" \
  --disable-nls \
  --enable-shared \
  --enable-gprofng=no \
  --disable-werror \
  --enable-64-bit-bfd \
  --enable-new-dtags \
  --enable-default-hash-style=gnu

make
make DESTDIR="$SYSROOT" install


# gcc
BUILDDIR="$BUILD/gcc2"
rm -rf "$BUILDDIR"
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"

"$SOURCES/gcc/configure" \
  --build="$GUESS" --host="$TARGET" --target="$TARGET" --prefix=/usr \
  --with-build-sysroot="$SYSROOT" \
  --enable-default-pie --enable-default-ssp \
  --disable-fixincludes \
  --disable-nls \
  --disable-multilib \
  --disable-libatomic --disable-libgomp --disable-libquadmath \
  --disable-libssp --disable-libvtv --disable-libsanitizer \
  --enable-languages=c,c++ \
  CXX_FOR_TARGET="$TARGET-gcc -nostdinc++" \
  target_configargs=gcc_cv_target_thread_file=posix


make
make DESTDIR="$SYSROOT" install



# NOTE: if it doesn't compile remove './build/ccstrap/build' and try again. you might also want try removing the unpacked src dirs
# TODO: finish this script. we need to build gcc stage 2 and binutils stage 2 and such
#       read the lfs book chapter 5

# TODO: turn this into a package recipe. It's probably going to be painful rewriting that in pure python 
#       so we could just make it call a bash script. i dont see a big problem with that
