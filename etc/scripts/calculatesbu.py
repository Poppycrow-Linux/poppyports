import os, subprocess
import pbuild
import time

print("Reading poppy-base dependencies")
recipe = {}
with open("main/poppy-base/recipe.py", "r") as f:
  exec(f.read(), recipe)

depends = recipe["depends"]
sbu_reference = "main/ncurses"
print(depends)

results = {}


def run_apk(*args):
    #env = os.environ.copy()
    #env["LD_LIBRARY_PATH"] = "staging/apk-install/lib/x86_64-linux-gnu/"
    subprocess.run(["apk"] + list(args), env=os.environ, check=True)

for dep in depends:
  print(f"building {dep}")

  if dep == "main/linux-stable":
    continue

  recipe = pbuild.read_recipe(f"{dep}/recipe.py")

  ctx = pbuild.BuildContext(os.path.abspath(f"build/pkg/{dep}"),os.path.abspath(f"{dep}"),recipe)

  ctx.NPROC = 1

  os.makedirs(ctx.BUILDDIR, exist_ok=True)

  outpath = f"{os.path.abspath(f"build/pkg/{dep}")}/{recipe['pkgname']}-{recipe['pkgver']}.apk"

  if os.path.exists(outpath):
    print(f"it already built. delete this packages folder in build if you want to rebuild this")
    continue

  skip_extracting = pbuild.download_files(ctx, recipe, False)
  if not skip_extracting:
    print("Extracting source...")
    pbuild.extract_src(ctx, recipe)

  start_time = time.time()

  ctx.build()
  ctx.install()

  results[dep] = time.time()-start_time

  run_apk("mkpkg",
          "-I", f"name:{recipe["pkgname"]}",
          "-I", f"version:{recipe["pkgver"]}",
          "-F", ctx.PKGDIR,
          "-o", outpath)

  #subprocess.run(["time","python3", "pbuild.py", f"{dep}", f"build/pkg/{dep}"])

print(results)
SBU = results["main/ncurses"]
print("SBU",sbu_reference,SBU)
for name, time in results.items():
  print(f"{name} {(time/SBU):.1f} SBUs ({time:.1f} seconds)")
