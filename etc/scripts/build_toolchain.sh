#!/usr/bin/env bash

set -euo pipefail

export LC_ALL=C
export MAKEFLAGS="${MAKEFLAGS:--j$(nproc)}"

die() {
  echo "E: $*" >&2
  exit 1
}

info() {
  echo "I: $*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

download() {
  local url="$1"
  local destination="$2"
  local checksum="${3:-}"

  if [[ -f "$destination" && -n "$checksum" ]]; then
    echo "$checksum  $destination" | sha256sum -c - >/dev/null 2>&1 || {
      info "checksum failed for $destination; downloading again"
      rm -f "$destination"
    }
  fi

  if [[ -f "$destination" ]]; then
    info "already downloaded: $destination"
    return
  fi

  info "downloading: $url"
  wget --continue --output-document="$destination" "$url"

  if [[ -n "$checksum" ]]; then
    echo "$checksum  $destination" | sha256sum -c -
  else
    info "warning: no checksum configured for $destination"
  fi
}

extract() {
  local archive="$1"
  local destination="$2"

  if [[ -f "$destination/.pbuild-extracted" ]]; then
    info "already extracted: $destination"
    return
  fi

  rm -rf "$destination"
  mkdir -p "$destination"

  info "extracting: $archive"
  tar -xf "$archive" -C "$destination" --strip-components=1

  touch "$destination/.pbuild-extracted"
}

build_directory() {
  local name="$1"

  rm -rf "$BUILD/$name"
  mkdir -p "$BUILD/$name"
  cd "$BUILD/$name"
}

derive_target() {
  local arch="$1"
  local libc="$2"
  local vendor="$3"
  local libc_suffix

  case "$libc" in
    glibc)
      libc_suffix="gnu"
      ;;
    musl)
      libc_suffix="musl"
      ;;
    *)
      die "unsupported libc: $libc"
      ;;
  esac

  case "$arch" in
    x86_64)
      echo "x86_64-${vendor}-linux-${libc_suffix}"
      ;;
    aarch64)
      echo "aarch64-${vendor}-linux-${libc_suffix}"
      ;;
    armv7)
      if [[ "$libc" == "glibc" ]]; then
        echo "arm-${vendor}-linux-gnueabihf"
      else
        echo "arm-${vendor}-linux-musleabihf"
      fi
      ;;
    i686)
      echo "i686-${vendor}-linux-${libc_suffix}"
      ;;
    riscv64)
      echo "riscv64-${vendor}-linux-${libc_suffix}"
      ;;
    ppc64le)
      echo "powerpc64le-${vendor}-linux-${libc_suffix}"
      ;;
    s390x)
      echo "s390x-${vendor}-linux-${libc_suffix}"
      ;;
    *)
      die "unsupported architecture: $arch"
      ;;
  esac
}

derive_kernel_arch() {
  case "$1" in
    x86_64|i686)
      echo "x86"
      ;;
    aarch64)
      echo "arm64"
      ;;
    armv7)
      echo "arm"
      ;;
    riscv64)
      echo "riscv"
      ;;
    ppc64le)
      echo "powerpc"
      ;;
    s390x)
      echo "s390"
      ;;
    *)
      die "cannot derive Linux kernel ARCH from: $1"
      ;;
  esac
}

default_slibdir() {
  local arch="$1"

  case "$arch" in
    x86_64)
      echo "/lib64"
      ;;
    *)
      echo "/lib"
      ;;
  esac
}

test_sysroot_compiler() {
  local compiler="$TOOLCHAIN/bin/$TARGET-gcc"
  local test_source="$BUILD/sysroot-test.c"
  local test_binary="$BUILD/sysroot-test"

  [[ -x "$compiler" ]] || die "compiler was not installed: $compiler"

  cat > "$test_source" <<'EOF'
int main(void) {
  return 0;
}
EOF

  info "compiler sysroot:"
  "$compiler" -print-sysroot

  info "building sysroot test binary"
  "$compiler" --sysroot="$SYSROOT" "$test_source" -o "$test_binary"

  if command -v file >/dev/null 2>&1; then
    file "$test_binary"
  fi

  if command -v readelf >/dev/null 2>&1; then
    info "requested program interpreter:"
    readelf -l "$test_binary" | grep -i "interpreter" || true

    info "dynamic dependencies:"
    readelf -d "$test_binary" | grep "NEEDED" || true
  fi

  rm -f "$test_source" "$test_binary"
}

ARCH="${ARCH:-x86_64}"
LIBC="${LIBC:-glibc}"
VENDOR="${VENDOR:-crow}"

TARGET="${TARGET:-$(derive_target "$ARCH" "$LIBC" "$VENDOR")}"
BUILD_TRIPLE="${BUILD_TRIPLE:-$(cc -dumpmachine)}"

PREFIX="${PREFIX:-$PWD/build/ccstrap}"
TOOLCHAIN="${TOOLCHAIN:-$PREFIX/toolchain}"
SYSROOT="${SYSROOT:-$PREFIX/sysroot}"
SOURCES="${SOURCES:-$PREFIX/srcs}"
BUILD="${BUILD:-$PREFIX/build}"

BINUTILS_VERSION="${BINUTILS_VERSION:-2.47}"
GCC_VERSION="${GCC_VERSION:-16.2.0}"
GLIBC_VERSION="${GLIBC_VERSION:-2.44}"
HEADERS_VERSION="${HEADERS_VERSION:-7.1.8}"

MIN_KERNEL="${MIN_KERNEL:-5.10}"
LIBC_SLIBDIR="${LIBC_SLIBDIR:-$(default_slibdir "$ARCH")}"

BINUTILS_SHA256="${BINUTILS_SHA256:-}"
GCC_SHA256="${GCC_SHA256:-}"
GLIBC_SHA256="${GLIBC_SHA256:-}"
HEADERS_SHA256="${HEADERS_SHA256:-}"

if [[ "${MULTILIB:-no}" == "yes" ]]; then
  die "this script currently builds one ABI per sysroot; use separate ARCH/SYSROOT values instead of enabling incomplete multilib support"
fi

for command in bash gcc g++ make bison flex gawk m4 perl python3 wget tar xz bzip2 gzip patch sed sha256sum; do
  require_command "$command"
done

mkdir -p "$PREFIX" "$TOOLCHAIN" "$SYSROOT" "$SOURCES" "$BUILD"

info "build triple: $BUILD_TRIPLE"
info "target triple: $TARGET"
info "architecture: $ARCH"
info "libc: $LIBC"
info "libc runtime directory: $LIBC_SLIBDIR"
info "toolchain: $TOOLCHAIN"
info "sysroot: $SYSROOT"
info "sources: $SOURCES"
info "build directories: $BUILD"

export PATH="$TOOLCHAIN/bin:$PATH"

BINUTILS_ARCHIVE="$SOURCES/binutils.tar.xz"
GCC_ARCHIVE="$SOURCES/gcc.tar.xz"
GLIBC_ARCHIVE="$SOURCES/glibc.tar.xz"
HEADERS_ARCHIVE="$SOURCES/linux.tar.xz"

BINUTILS_SOURCE="$SOURCES/binutils"
GCC_SOURCE="$SOURCES/gcc"
GLIBC_SOURCE="$SOURCES/glibc"
HEADERS_SOURCE="$SOURCES/linux"

download "https://ftp.gnu.org/gnu/binutils/binutils-${BINUTILS_VERSION}.tar.xz" "$BINUTILS_ARCHIVE" "$BINUTILS_SHA256"
download "https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.xz" "$GCC_ARCHIVE" "$GCC_SHA256"
download "https://ftp.gnu.org/gnu/glibc/glibc-${GLIBC_VERSION}.tar.xz" "$GLIBC_ARCHIVE" "$GLIBC_SHA256"
download "https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-${HEADERS_VERSION}.tar.xz" "$HEADERS_ARCHIVE" "$HEADERS_SHA256"

extract "$BINUTILS_ARCHIVE" "$BINUTILS_SOURCE"
extract "$GCC_ARCHIVE" "$GCC_SOURCE"
extract "$GLIBC_ARCHIVE" "$GLIBC_SOURCE"
extract "$HEADERS_ARCHIVE" "$HEADERS_SOURCE"

if [[ ! -f "$GCC_SOURCE/.pbuild-prerequisites" ]]; then
  info "downloading GCC prerequisites"
  cd "$GCC_SOURCE"
  ./contrib/download_prerequisites --no-verify
  touch "$GCC_SOURCE/.pbuild-prerequisites"
fi

KERNEL_ARCH="$(derive_kernel_arch "$ARCH")"

info "building cross Binutils"
build_directory "binutils"

"$BINUTILS_SOURCE/configure" \
  --build="$BUILD_TRIPLE" \
  --host="$BUILD_TRIPLE" \
  --target="$TARGET" \
  --prefix="$TOOLCHAIN" \
  --with-sysroot="$SYSROOT" \
  --disable-nls \
  --disable-werror \
  --disable-gprofng \
  --enable-new-dtags

make
make install

info "building stage-1 cross GCC"
build_directory "gcc-stage1"

"$GCC_SOURCE/configure" \
  --build="$BUILD_TRIPLE" \
  --host="$BUILD_TRIPLE" \
  --target="$TARGET" \
  --prefix="$TOOLCHAIN" \
  --with-sysroot="$SYSROOT" \
  --with-glibc-version="$GLIBC_VERSION" \
  --without-headers \
  --disable-shared \
  --disable-threads \
  --disable-nls \
  --disable-fixincludes \
  --disable-libatomic \
  --disable-libgomp \
  --disable-libquadmath \
  --disable-libssp \
  --disable-libvtv \
  --with-newlib \
  --disable-libstdcxx \
  --enable-languages=c \
  --disable-multilib

make all-gcc all-target-libgcc
make install-gcc install-target-libgcc

info "installing Linux userspace headers"
cd "$HEADERS_SOURCE"
make mrproper
make ARCH="$KERNEL_ARCH" headers_install INSTALL_HDR_PATH="$SYSROOT/usr"

info "building Glibc"
build_directory "glibc"

export CC="$TARGET-gcc"
export CXX="$TARGET-g++"
export AR="$TARGET-ar"
export RANLIB="$TARGET-ranlib"
export NM="$TARGET-nm"

"$GLIBC_SOURCE/configure" \
  --prefix=/usr \
  --build="$BUILD_TRIPLE" \
  --host="$TARGET" \
  --with-headers="$SYSROOT/usr/include" \
  --enable-kernel="$MIN_KERNEL" \
  --disable-nscd \
  --disable-werror \
  libc_cv_slibdir="$LIBC_SLIBDIR"

make
make DESTDIR="$SYSROOT" install

unset CC
unset CXX
unset AR
unset RANLIB
unset NM

info "building final cross GCC"
build_directory "gcc-final"

"$GCC_SOURCE/configure" \
  --build="$BUILD_TRIPLE" \
  --host="$BUILD_TRIPLE" \
  --target="$TARGET" \
  --prefix="$TOOLCHAIN" \
  --with-sysroot="$SYSROOT" \
  --with-build-sysroot="$SYSROOT" \
  --with-native-system-header-dir=/usr/include \
  --enable-languages=c,c++ \
  --enable-shared \
  --enable-threads=posix \
  --enable-default-pie \
  --enable-default-ssp \
  --disable-nls \
  --disable-fixincludes \
  --disable-bootstrap \
  --disable-multilib

make
make install

info "cleaning temporary compiler files"
rm -rf "$SYSROOT/tools"

info "testing generated cross compiler"
test_sysroot_compiler

info "toolchain completed successfully"
info "compiler: $TOOLCHAIN/bin/$TARGET-gcc"
info "sysroot: $SYSROOT"
