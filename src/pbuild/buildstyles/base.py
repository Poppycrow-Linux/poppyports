## This is the base BuildStyle.
## A BuildStyle defines how a package is built.
## This is helpful to not write out how to build something with Make or Configure for 9000th time.
## This also has the convinience of being able to not even care about things like cross-compilation and is a much better design than make or configure helper function inside buildcontext (it is already fat enough as is).
class BuildStyle:
  name = None

  def __init__(self, context):
    self.c = context
    self.recipe = context.recipe

  def prepare(self):
    pass ## this is where the preparations happen in special cases. most notably, patching happens there. if you need to patch things later for some reason, call a buildcontext helper.

  def configure(self):
    pass ## this is where the configuration happens

  def build(self):
    pass

  def check(self):
    pass ## this is where tests are run (if present)

  def install(self):
    pass

  def run(self):
    self.prepare()
    self.configure()
    self.build()
    self.check()
    self.install()
