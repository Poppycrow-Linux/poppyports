# TODO: separate this to llvm-clang, llvm-libcpp, llvm-utils and such? which also means TODO: reduce sources duplication somehow if we can to save some storage and bandwidth.

# now, to clear up regarding this package because valera might be asking:
# yes, building a system AROUND libc++ can kind of maybe introduce ABI bugs with libstdc++, that does not mean they cannot peacefully coexist
# they are completely different dynamic objects that have zero coorelation between eachother. in fact, clang++ by default literally links with gnu stdc++ on linux anyway!!!
# try it yourself:
#   echo 'int main() {}' > a.cc
#   clang++ a.cc && ldd ./a.out
#   g++ a.cc && ldd ./a.out

recipever = 0
pkgname = "llvm"
pkgver = "22.1.8"
pkgrel = 0
pkgdesc = "LLVM Project - Low Level Virtual Machine"
url = "https://llvm.org/"
arch = "all"
license = "Apache-2.0"
maintainer = "samxyz30"

sources = [f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{pkgver}/llvm-project-{pkgver}.src.tar.xz"]
depends = []

def build(c):
  c.SRCDIR += f"/llvm-project-{pkgver}.src"

  c.sh("mkdir", "-p", f"{c.SRCDIR}/build")
  c.SRCDIR += "/build"

  c.sh("cmake", 
       "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={c.PKGDIR}",
       "-DBUILD_SHARED_LIBS=ON",
       "-DLLVM_ENABLE_PROJECTS=clang",
       #"-DLLVM_ENABLE_RUNTIMES=libcxx;libcxxabi",
       "-DLLVM_USE_LINKER=lld",
       "../llvm")

  c.sh("cmake", "--build", ".", f"-j{c.NPROC}")


def install(c):
  c.sh("cmake", "--install", ".")
