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

  # Sanity-check the archive before trusting a partial download.
  tar -tf "$archive" >/dev/null 2>&1 || die "archive is corrupt or incomplete: $archive"

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

  case "$arch" in # I ONLY TESTED ARM64. i added more just for Fun. if you get poppycrow running on ppc and something broke then I am Sorry. TODO: make this cleaner
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

derive_kernel_arch() { # this is needed because the linux kernbel are a bunch of idiots who use different names than the triplet
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
    ppc64le|s390x)
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
  "$compiler" \
  "${TARGET_CFLAGS[@]}" \
  --sysroot="$SYSROOT" \
  "$test_source" \
  -o "$test_binary"

  if command -v file >/dev/null 2>&1; then
    file "$test_binary"
  fi

  if command -v readelf >/dev/null 2>&1; then
    info "requested program interpreter:"
    readelf -l "$test_binary" | grep -i "interpreter" || true

    info "dynamic dependencies:"
    readelf -d "$test_binary" | grep "NEEDED" || true

    local interp
    interp="$(readelf -l "$test_binary" 2>/dev/null \
      | awk '/interpreter/ {print $NF; exit}')"
    if [[ -n "$interp" && "$interp" == *"$SYSROOT"* ]]; then
      die "sysroot is not relocatable: PT_INTERP contains the build sysroot ($interp)"
    fi
    info "PT_INTERP: ${interp:-(none)} (sysroot-relative: ok)"
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
LIBC_RTLDDIR="${LIBC_RTLDDIR:-$LIBC_SLIBDIR}"

GCC_SYSROOT_DEFAULT="${GCC_SYSROOT_DEFAULT:-$SYSROOT}"

GCC_TARGET_CONFIGURE_ARGS=()
TARGET_CFLAGS=(-O2) # this is set explicitly because otherwise gcc will throw a hissy fit about not having compiler optimizations on.

case "$LIBC" in
  glibc)
    ;;
  musl)
    die "LIBC=musl is not implemented; this script currently builds glibc only"
    ;;
  *)
    die "unsupported libc: $LIBC"
    ;;
esac

# libc_slibdir / libc_rtlddir must be sysroot-relative paths. if they
# contain the build sysroot or prefix, glibc bakes a host-absolute path
# into ld.so and the resulting sysroot cannot be copied and stuff which SUCKS
for var in LIBC_SLIBDIR LIBC_RTLDDIR; do
  local_val="${!var}"
  case "$local_val" in
    /*) : ;;
    *)  die "$var must be an absolute sysroot path, got: $local_val" ;;
  esac
  case "$local_val" in
    *"$SYSROOT"*|*"$PREFIX"*) die "$var must not contain the sysroot or prefix path: $local_val" ;;
  esac
done
unset local_val

case "$ARCH" in # once again i only properly tested aarch64 but the others are also supposed to work
# things are taken from:
# https://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html
# https://www.linuxfromscratch.org/~xry111/lfs/view/arm64/chapter05/gcc-pass1.html (arm64 lfs)
# https://aur.archlinux.org/packages/arm-linux-gnueabihf-glibc?O=10 - glibc for armv7
  x86_64)
    # it already assumes x86_64 #lol
    ;;

  aarch64)
    GCC_TARGET_CONFIGURE_ARGS+=(
      --with-arch=armv8-a
      --with-abi=lp64
    )
    TARGET_CFLAGS+=(
      -march=armv8-a
      -mabi=lp64
    )
    ;;

  armv7)
    # The gnueabihf target requires the hard-float ABI.
    GCC_TARGET_CONFIGURE_ARGS+=(
      --with-arch=armv7-a
      --with-fpu=vfpv3-d16
      --with-float=hard
    )
    TARGET_CFLAGS+=(
      -march=armv7-a
      -mfpu=vfpv3-d16
      -mfloat-abi=hard
    )
    ;;

  i686)
    GCC_TARGET_CONFIGURE_ARGS+=(
      --with-arch=i686
    )
    TARGET_CFLAGS+=(
      -march=i686
    )
    ;;

  riscv64)
    GCC_TARGET_CONFIGURE_ARGS+=(
      --with-arch=rv64gc
      --with-abi=lp64d
    )
    TARGET_CFLAGS+=(
      -march=rv64gc
      -mabi=lp64d
    )
    ;;

  ppc64le|s390x)
    # the target triples select the required 64-bit ABI and endianness.
    ;;

  *)
    die "unsupported architecture: $ARCH"
    ;;
esac

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
info "libc loader directory:  $LIBC_RTLDDIR"
info "toolchain: $TOOLCHAIN"
info "sysroot: $SYSROOT"
info "gcc default sysroot: $GCC_SYSROOT_DEFAULT"
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

download "http://ftp-stud.fht-esslingen.de/pub/Mirrors/ftp.gnu.org/binutils/binutils-${BINUTILS_VERSION}.tar.xz" "$BINUTILS_ARCHIVE" "$BINUTILS_SHA256"
download "http://ftp-stud.fht-esslingen.de/pub/Mirrors/ftp.gnu.org/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.xz" "$GCC_ARCHIVE" "$GCC_SHA256"
download "http://ftp-stud.fht-esslingen.de/pub/Mirrors/ftp.gnu.org/glibc/glibc-${GLIBC_VERSION}.tar.xz" "$GLIBC_ARCHIVE" "$GLIBC_SHA256"
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
  --with-sysroot="$GCC_SYSROOT_DEFAULT" \
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
  --with-sysroot="$GCC_SYSROOT_DEFAULT" \
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
  --disable-multilib \
  "${GCC_TARGET_CONFIGURE_ARGS[@]}"
  # todo: enable multilib and make it work!

make all-gcc all-target-libgcc
make install-gcc install-target-libgcc

info "installing Linux userspace headers"

##debug slop
info "shell ARCH: ${ARCH:-unset}"
info "kernel ARCH: $KERNEL_ARCH"

[[ -f "$HEADERS_SOURCE/arch/$KERNEL_ARCH/Makefile" ]] || die \
  "missing kernel architecture Makefile: arch/$KERNEL_ARCH/Makefile"

## linux kernel is an IDIOT and looks at arch variable first.
make -C "$HEADERS_SOURCE" \
  ARCH="$KERNEL_ARCH" \
  mrproper

make -C "$HEADERS_SOURCE" \
  ARCH="$KERNEL_ARCH" \
  headers_install \
  INSTALL_HDR_PATH="$SYSROOT/usr"

info "building Glibc"
build_directory "glibc"

export CC="$TARGET-gcc"
export CXX="$TARGET-g++"
export AR="$TARGET-ar"
export RANLIB="$TARGET-ranlib"
export NM="$TARGET-nm"

# libc_cv_slibdir and libc_cv_rtlddir are pinned to *sysroot-relative*
# paths so glibc does not bake the build sysroot into ld.so or libc.so.
# Without libc_cv_rtlddir, glibc's default can leak the sysroot path
# under some cross-compile configurations.
CFLAGS="${CFLAGS:-} ${TARGET_CFLAGS[*]}" \
"$GLIBC_SOURCE/configure" \
  --prefix=/usr \
  --build="$BUILD_TRIPLE" \
  --host="$TARGET" \
  --with-headers="$SYSROOT/usr/include" \
  --enable-kernel="$MIN_KERNEL" \
  --disable-nscd \
  --disable-werror \
  libc_cv_slibdir="$LIBC_SLIBDIR" \
  libc_cv_rtlddir="$LIBC_RTLDDIR"

make
make DESTDIR="$SYSROOT" install

unset CC
unset CXX
unset AR
unset RANLIB
unset NM

# NOW I HAVE TO DO SYMLINKS A DIFFERENT WAY THANKS TO OVERLAYFS. LONG LIVE OVERLAYFS

merge_into_usr() {
  local name="$1"
  local root_path="$SYSROOT/$name"
  local usr_path="$SYSROOT/usr/$name"

  # we only do top level dirs fuck off
  case "$name" in
    */*) die "merge_into_usr: invalid name: $name" ;;
  esac

  [[ -e "$root_path" || -L "$root_path" ]] || return 0

  if [[ -L "$root_path" ]]; then
    local current
    current="$(readlink "$root_path")"
    if [[ "$current" != "usr/$name" ]]; then
      die "/$name is a symlink to '$current', expected 'usr/$name'"
    fi
    info "already merged: /$name -> usr/$name"
    return 0
  fi

  [[ -d "$root_path" ]] || die "cannot merge /$name: not a directory"

  #
  local root_real usr_real
  root_real="$(readlink -f "$root_path" 2>/dev/null || true)"
  usr_real="$(readlink -f "$usr_path"  2>/dev/null || true)"

  if [[ -n "$root_real" && "$root_real" == "$usr_real" ]]; then
    info "/$name and /usr/$name already resolve to the same directory; skipping copy"
  else
    mkdir -p "$usr_path"
    # -a preserves perms/symlinks/timestamps. overwrite is fine because
    # glibc installs identical content into /usr and /usr/whatever
    cp -a "$root_path/." "$usr_path/"
  fi

  rm -rf "$root_path"
  ln -s "usr/$name" "$root_path"
  info "merged: /$name -> usr/$name"
}

merge_into_usr lib64
merge_into_usr lib
merge_into_usr bin
merge_into_usr sbin

# ensure that /usr/POOP is areal folder
for d in lib lib64 bin sbin; do
  if [[ -L "$SYSROOT/usr/$d" ]]; then
    die "/usr/$d is still a symlink, you fucked up"
  fi
done

for script in "$SYSROOT"/usr/lib/libc.so "$SYSROOT"/usr/lib/libc.so.6; do
  [[ -f "$script" ]] || continue
  head -c 256 "$script" | grep -q 'GNU ld script' || continue
  while IFS= read -r ref; do
    [[ -e "$SYSROOT$ref" ]] || die "$script references missing $ref"
  done < <(grep -oE '/[A-Za-z0-9._/-]+' "$script")
done

# this shit is done to make sure sysroot does not break when moved after compilation
info "auditing sysroot for host-absolute paths"

hits="$(grep -rIl -F "$SYSROOT" "$SYSROOT" 2>/dev/null \
  | grep -v '/\.pbuild-extracted$' \
  | grep -v '/\.pbuild-sysroot-info$' \
  || true)"

if [[ -n "$hits" ]]; then
  info "files referencing the build sysroot path:"
  printf '  %s\n' "$hits"
  die "sysroot is not relocatable: host paths baked into text files"
fi

# ld.so.conf and friends must reference /usr, /lib
for f in "$SYSROOT"/etc/ld.so.conf "$SYSROOT"/etc/ld.so.conf.d/*; do
  [[ -e "$f" ]] || continue
  if grep -qF "$SYSROOT" "$f"; then
    sed -i "s|$SYSROOT||g" "$f"
    info "rewrote host paths in $f"
  fi
done


info "building final cross GCC"
build_directory "gcc-final"

"$GCC_SOURCE/configure" \
  --build="$BUILD_TRIPLE" \
  --host="$BUILD_TRIPLE" \
  --target="$TARGET" \
  --prefix="$TOOLCHAIN" \
  --with-sysroot="$GCC_SYSROOT_DEFAULT" \
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
  --disable-multilib \
  "${GCC_TARGET_CONFIGURE_ARGS[@]}"

make
make install

info "cleaning temporary compiler files"
rm -rf "$SYSROOT/tools"

info "testing generated cross compiler"
test_sysroot_compiler

info "toolchain completed successfully"
info "compiler: $TOOLCHAIN/bin/$TARGET-gcc"
info "sysroot: $SYSROOT"

#TODO: clean this script up, maybe rewrite it in pytho.
