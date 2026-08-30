from .base import BuildStyle
import subprocess
import os


## this template is used to build generic linuxes. also can copy the bzimages over to /boot if you so desire

class KernelStyle(BuildStyle):
  name = "kernel"

  def make_args(self):
    return [f"O={self.c.workdir()}/build", f"ARCH={self.c.kernel_arch()}", f"CROSS_COMPILE={self.c.TRIPLE}-"]

  def configure(self):
    self.c.sh(f"mkdir -p {self.c.workdir()}/build")
    args = self.make_args()
    config = self.recipe.get("kernel_config")

    if config is not None:
      config_path = config
      if not config_path.startswith("/"):
        config_path = f"{self.c.PORTDIR}/{config}"

      self.c.sh("cp", config_path, f"{self.c.workdir()}/build/.config", cwd=self.c.workdir())
      self.c.sh("make", *args, "olddefconfig", cwd=self.c.workdir())  # cachewave doesn't know how to migrate old configs to new kernels. it's okay.
      return

    defconfig = self.recipe.get("kernel_defconfig", "defconfig")
    self.c.sh("make", *args, defconfig, cwd=self.c.workdir())

  def build(self):
    args = self.make_args()
    args.extend(self.recipe.get("kernel_make_args", []))

    targets = self.recipe.get("kernel_make_targets", [])
    if isinstance(targets, str):
      targets = [targets]

    targets = [target for target in targets if target]

    if not targets:
      targets = [self.image_target()]

      if self.recipe.get("kernel_install_modules", True):
        targets.append("modules")

    self.c.sh("make", *args, f"-j{self.c.NPROC}", *targets, cwd=self.c.workdir())

  def check(self):
    if not self.recipe.get("make_check", False):
      return

    args = self.make_args()
    target = self.recipe.get("make_check_target", "kselftest")
    self.c.sh("make", *args, target, cwd=self.c.workdir())

  def kernel_release(self):
    return subprocess.check_output(["make", *self.make_args(), "-s", "kernelrelease"], cwd=self.c.workdir(), env=self.c.env, text=True).strip()

  def install(self):
    args = self.make_args()
    release = self.kernel_release()

    if self.recipe.get("kernel_install_image", True):
      image = self.image_path()

      if image is None or not os.path.isfile(image):
        raise RuntimeError(f"kernel image was not built: {image}")

      self.c.sh("install", "-Dm644", image, f"{self.c.PKGDIR}/boot/vmlinuz-{release}")

      config = os.path.join(f"{self.c.workdir()}/build", ".config")
      if os.path.isfile(config):
        self.c.sh("install", "-Dm644", config, f"{self.c.PKGDIR}/boot/config-{release}")

      system_map = os.path.join(f"{self.c.workdir()}/build", "System.map")
      if os.path.isfile(system_map):
        self.c.sh("install", "-Dm644", system_map, f"{self.c.PKGDIR}/boot/System.map-{release}")

    if self.recipe.get("kernel_install_modules", True):
      self.c.sh("make", *args, f"INSTALL_MOD_PATH={self.c.PKGDIR}", "DEPMOD=true", "modules_install", cwd=self.c.workdir())
      modules_dir = os.path.join(self.c.PKGDIR, "lib", "modules", release)
      # we KILL symlinks to build and source because they don't work and should not be packaged'
      for link in ("build", "source"):
        link_path = os.path.join(modules_dir, link)
        if os.path.lexists(link_path):
          if not os.path.islink(link_path):
            raise RuntimeError(f"kernel module path is not a symlink: {link_path}")
          os.unlink(link_path)

    if self.recipe.get("kernel_install_firmware", False):
      self.c.sh("make", *args, f"INSTALL_FW_PATH={self.c.PKGDIR}/lib/firmware", "firmware_install", cwd=self.c.workdir())

  def image_target(self):
    targets = {
      "x86_64": "bzImage",
      "i686": "bzImage",
      "aarch64": "Image",
      "armv7": "zImage",
      "riscv64": "Image",
      "ppc64le": "vmlinux",
      "s390x": "bzImage",
    }

    try:
      return targets[self.c.ARCH]
    except KeyError as error:
      raise RuntimeError(f"no kernel image target for {self.c.ARCH}") from error

  def image_path(self):
    paths = {
      "x86_64": "arch/x86/boot/bzImage",
      "i686": "arch/x86/boot/bzImage",
      "aarch64": "arch/arm64/boot/Image",
      "armv7": "arch/arm/boot/zImage",
      "riscv64": "arch/riscv/boot/Image",
      "ppc64le": "vmlinux",
      "s390x": "arch/s390/boot/bzImage",
    }

    try:
      image = paths[self.c.ARCH]
    except KeyError as error:
      raise RuntimeError(f"no kernel image path for {self.c.ARCH}") from error

    return os.path.join(f"{self.c.workdir()}/build", image)
