import argparse
import os

REQUIRED_KEYS = {"sources", "pkgname", "build", "install", "arch", "pkgver"}


class Colors:
    ERROR = "\x1b[5;97;101m"
    WARNING = "\x1b[5;30;103m"
    SUCCESS = "\x1b[0;97;48;5;28m"
    SH_COMMAND = "\x1b[0;97;48;5;21m"
    END = "\x1b[0m"
    UNPACKAGED = "\x1b[30;43m"


def log(color, *args):
    print(f"{color or ''}I:", *args, Colors.END)


def read_recipe(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        exec(f.read(), data)

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        print(f"{path}: missing key(s): {', '.join(sorted(missing))}")
    return data

#TODO: make all of that an import thing

def find_recipe_dirs(root):
    if not os.path.isdir(root):
        raise FileNotFoundError(f"Directory does not exist: {root}")

    recipe_dirs = []
    for category_name in os.listdir(root):
        category_dir = os.path.join(root, category_name)
        if not os.path.isdir(category_dir):
            continue

        for package_name in os.listdir(category_dir):
            package_dir = os.path.join(category_dir, package_name)
            if os.path.isdir(package_dir):
                recipe_dirs.append(package_dir)

    return recipe_dirs


def main():
    parser = argparse.ArgumentParser(
        prog="whattopackage",
        description="Helper utility for seeing what package dependencies are missing.",
        epilog="See more @ https://codeberg.org/Poppycrow-Linux/poppyports",
    )
    parser.add_argument(
        "-u", "-uo", "--unpackaged-only",
        action="store_true",
        help="Show only packages with unresolved dependencies",
    )
    parser.add_argument(
        "-d", "--dir",
        default="./recipes",
        help="Root recipes directory containing category folders",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.dir)

    try:
        recipe_dirs = find_recipe_dirs(root)
    except FileNotFoundError as e:
        print(e)
        return

    recipe_names = {os.path.basename(p) for p in recipe_dirs}
    recipe_names.add("libc") # libc is already packaged

    totalmissing = set([])

    for recipe_dir in recipe_dirs:
        recipe_file = os.path.join(recipe_dir, "recipe.py")
        if not os.path.isfile(recipe_file):
            print(f"Warning: missing recipe file: {recipe_file}")
            continue

        recipe = read_recipe(recipe_file)
        pkgname = os.path.basename(recipe_dir)

        deps = (
            recipe.get("depends", [])
            + recipe.get("makedepends", [])
            + recipe.get("optdepends", [])
        )

        missing = [dep for dep in deps if dep.split("/")[-1] not in recipe_names]
        for i in missing: totalmissing.add(i)

        if missing:
            log(Colors.UNPACKAGED, f"{pkgname} depends on {', '.join(missing)}, which needs to be packaged!")
        elif not args.unpackaged_only:
            if deps:
                log(Colors.SUCCESS, f"{pkgname} is fully packaged, unless you forgot to mention all of its dependencies.")
            else:
                log(Colors.SH_COMMAND, f"{pkgname} has no declared dependencies. Are you sure you are not forgetting something?")
    print("IN TOTAL:")
    print(*totalmissing)

if __name__ == "__main__":
    main()
