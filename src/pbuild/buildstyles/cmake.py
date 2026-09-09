from .base import BuildStyle
from ..crossutils import write_cmake_toolchain

class CMakeStyle(BuildStyle):
  name = "cmake"

  def configure(self):
    args = [
      "cmake",
      "-B", self.c.builddir(),
      "-S", self.c.workdir(),
      "-DCMAKE_INSTALL_PREFIX=/usr",
      "-DCMAKE_BUILD_TYPE=Release",
    ]

    if self.c.SYSROOT is not None:
      toolchain = write_cmake_toolchain(self.c.SYSROOT, self.c.BUILDDIR, self.c.ARCH, self.c.CC, self.c.CXX, self.c.AR, self.c.RANLIB, self.c.STRIP)

      if toolchain is not None:
        args.extend(["-DCMAKE_TOOLCHAIN_FILE=" + toolchain])

    args.extend(self.recipe.get("configure_args", []))
    self.c.sh(*args, cwd=self.c.workdir())

  def build(self):
    args = ["cmake", "--build", self.c.builddir(), "-j" + str(self.c.NPROC)]
    args.extend(self.recipe.get("make_build_args", []))
    self.c.sh(*args, cwd=self.c.workdir())

  def check(self):
    if not self.recipe.get("make_check", True):
      return

    args = ["cmake", "--build", self.c.builddir(), "--target", "test"]
    self.c.sh(*args, cwd=self.c.workdir())

  def install(self):
    if "install" in self.recipe:
      self.recipe["install"](self)
      return

    args = ["cmake", "--install", self.c.builddir(), "--prefix", "/usr", "--destdir", self.c.PKGDIR]
    args.extend(self.recipe.get("make_install_args", []))
    self.c.sh(*args, cwd=self.c.workdir())
