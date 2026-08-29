from .base import BuildStyle


class GnuConfigureStyle(BuildStyle):
  name = "gnu_configure"

  def configure(self):
    for command in self.recipe.get("configure_gen", []): # sometimes you have to work for the configure to appear. like those fuckass autogen.sh files.
      self.c.sh(command, cwd=self.c.workdir())

    args = [
      "./configure",
      f"--build={self.c.TRIPLE}",
      f"--host={self.c.HOST_TRIPLE}",
      "--prefix=/usr",
    ]

    args.extend(self.recipe.get("configure_args", [])) #take 5 guesses what it does
    self.c.sh(*args, cwd=self.c.workdir())

  def build(self):
    self.c.sh(
      "make",
      f"-j{self.c.NPROC}",
      *self.recipe.get("make_args", []), ## make build args are separate because gnu software is the kind of software to ask you to config stuff both in configure and make
      cwd=self.c.workdir(),
    )

  def check(self):
    if self.recipe.get("make_check", True):
      self.c.sh(
        "make",
        self.recipe.get("make_check_target", "check"),
        cwd=self.c.workdir(),
      )

  def install(self):
    if "install" in self.recipe:
      self.recipe["install"](self)
      return

    self.c.sh(
      "make",
      f"DESTDIR={self.c.PKGDIR}",
      "install",
      *self.recipe.get("make_install_args", []),
      cwd=self.c.workdir()
      )
