import os
import argparse
REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"}
script_dir = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(
                    prog='whattopackage',
                    #suggest_on_error=True, # this doesn't work on my python 3.13
                    description='Helper utility for seeing what package dependencies are missing.',
                    epilog='See more @ github.com/Poppycrow-Linux/poppyports/')
parser.add_argument('-unpackaged_only', '-u', '-uo', help='Show only packages with not all of the dependencies resolved', action="store_true")
args = parser.parse_args()
unpackagedonly = args.unpackaged_only


#TODO: make the repo look for files in the repo folder which will then have all categories in place
recipefolders = [
    os.path.join(script_dir, "main"),
    os.path.join(script_dir, "editors"),
    os.path.join(script_dir, "lang"),
    os.path.join(script_dir, "xorg"),
    os.path.join(script_dir, "apps"),
    os.path.join(script_dir, "games")
]


# ANSI colors and printing
class Colors:
  ERROR = "\x1b[5;97;101m"
  WARNING = "\x1b[5;30;103m"
  SUCCESS = "\x1b[0;97;48;5;28m"
  SH_COMMAND = "\x1b[0;97;48;5;21m"
  END = "\x1b[0m"
  UNPACKAGED = "\033[1;37;45m"

def log(clr: Colors, *args):
    print(f"{clr if (clr is not None) else ''}I:", *args, Colors.END)

def read_recipe(path):
    with open(path, "r", encoding="utf-8") as f:
        recipe_def = {}
        exec(f.read(), recipe_def)

    recipe_keys = set(recipe_def.keys())
    missing_keys = REQUIRED_KEYS - recipe_keys
    if missing_keys:
        print(f"This recipe is missing the {', '.join(sorted(missing_keys))} key(s)!")
    return recipe_def


recipelist = []

for folder in recipefolders:
    if not os.path.isdir(folder):
        print(f"Warning: directory does not exist: {folder}")
        continue

    recipelist.extend(
        [
            os.path.join(folder, item)
            for item in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, item))
        ]
    )

recipe_names = {os.path.basename(path) for path in recipelist}

for recipe_dir in recipelist:
    recipe = read_recipe(os.path.join(recipe_dir, "recipe.py"))
    pkgname = os.path.basename(recipe_dir)
    missingdeps = []
    fulldeps = recipe.get("depends", []) + recipe.get("makedepends", []) + recipe.get("optdepends", [])
    for dep in fulldeps:
        if dep.split("/")[-1] not in recipe_names:
            missingdeps.append(dep)
    if len(missingdeps) == 0:
        if not(unpackagedonly):
            if fulldeps != []:
                log(Colors.SUCCESS,f"{pkgname} is fully packaged, unless you forgot to mention all of its dependencies.")
            else:
                log(Colors.SH_COMMAND, f"{pkgname} has no declared dependencies. Are you sure you are not forgetting something?")
    else:
        log(Colors.UNPACKAGED ,f"{pkgname} depends on {", ".join(missingdeps)}, which needs to be packaged!")
