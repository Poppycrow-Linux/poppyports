from .base import BuildStyle


class KernelHeadersStyle(BuildStyle):
  name = "kernel_headers"

  def build(self):
    kernel_arch = self.c.kernel_arch()
    cross_compile = f"{self.c.TRIPLE}-"

    self.c.sh(
      "make",
      f"ARCH={kernel_arch}",
      f"CROSS_COMPILE={cross_compile}",
      "mrproper",
      cwd=self.c.workdir(),
    )

    self.c.sh(
      "make",
      f"ARCH={kernel_arch}",
      f"CROSS_COMPILE={cross_compile}",
      f"INSTALL_HDR_PATH={self.c.PKGDIR}/usr",
      "headers_install",
      cwd=self.c.workdir(),
    )

  def install(self):
    pass
