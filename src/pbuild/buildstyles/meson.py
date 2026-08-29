from .base import BuildStyle


class MesonStyle(BuildStyle):
  name = "meson"

  def configure(self):
    builddir = self.c.builddir()
    args = [
      "meson",
      "setup",
      builddir,
      self.c.workdir()
    ]

    cross_file = self.c.write_meson_cross_file()
    if cross_file is not None:
      args.extend(["--cross-file", cross_file]) ## meson is an IDIOT and needs a cross file

    args.extend(self.recipe.get("meson_args", [])) # this is where we apply more params via meson_args
    self.c.sh(*args, cwd=self.c.workdir())

  def build(self):
    self.c.sh("meson", "compile", "-C", self.c.builddir(), f"-j{self.c.NPROC}")

  def check(self):
    if self.recipe.get("make_check", True):
      self.c.sh("meson", "test", "-C", self.c.builddir())

  def install(self):
    if "install" in self.recipe:
      self.recipe["install"](self) ## this is a special case fallback
      return

    self.c.sh("meson", "install", "-C", self.c.builddir(), "--destdir", self.c.PKGDIR)
