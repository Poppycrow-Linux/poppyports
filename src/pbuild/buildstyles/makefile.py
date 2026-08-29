from .base import BuildStyle


class MakefileStyle(BuildStyle):
  def build(self):
    self.c.sh("make", f"-j{self.c.NPROC}", *self.recipe.get("make_args", []), cwd=self.c.workdir())

  def install(self):
    self.c.sh("make", f"-j{self.c.NPROC}", "DESTDIR=" + self.c.PKGDIR, "install", *self.recipe.get("make_install_args", []), cwd=self.c.workdir())
