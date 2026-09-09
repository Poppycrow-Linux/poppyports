## This is the base BuildStyle.
## A BuildStyle defines how a package is built.
## This is helpful to not write out how to build something with Make or Configure for 9000th time.
## This also has the convinience of being able to not even care about things like cross-compilation and is a much better design than make or configure helper function inside buildcontext (it is already fat enough as is).
class BuildStyle:
  name = None

  def __init__(self, context):
    global ctx
    self.c = context
    self.recipe = context.recipe

  def prepare(self, **kwargs):
    pass ## this is where the preparations happen in special cases. most notably, patching happens there. if you need to patch things later for some reason, call a buildcontext helper.

  def configure(self, **kwargs):
    pass ## this is where the configuration happens

  def build(self, **kwargs):
    pass

  def check(self, **kwargs):
    pass ## this is where tests are run (if present)

  def install(self, **kwargs):
    pass

  def run(self, **kwargs):
    for i in "prepare", "configure", "build", "check", "install":
      if i in self.recipe:
        self.recipe[i](self.c)
      else:
        i = getattr(self, i)
        i()
