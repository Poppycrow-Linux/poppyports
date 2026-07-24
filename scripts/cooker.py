import hashlib,requests,pathlib
print("Welcome to Cooker v0.000001. We hope you enjoy your recipe.\nPlease run from the root of the repo if you haven't.\n\n")
pkgname = input("Package Name:")
pkgver  = input("Version:")
pkgdesc = input("Description:")
url = input("URL (leave empty if none):")
license = input("License:")
sources = input("Sources (Separate by | to add multiple):").split('|')
#generate_hash = input("Would you like to automatically generate hashes for sources? (Will take time!) (y/N):")[0].lower() == "y"
generate_hash = False
depends = input("Dependencies (Separate by | to add multiple):").split('|')
makedepends = input("Make Dependencies (Separate by | to add multiple):").split('|')
print()
build_cmd = input("Build Command:")
install_cmd = input("Install Command:")
print()
is_main = input("Should this be a Main package? (y/N):")[0].lower() == "y"
directory = pathlib.Path(f'./{"main" if is_main else "extra"}/{pkgname}/')
directory.mkdir(parents=True,exist_ok=True)
path = directory / "recipe.py"
#FIXME: fix this. outputs wrong output 
def generate_sha256(sources):
    result = []
    for s in sources:
        response = requests.get(url)
        result.append(hashlib.sha256(response.content).hexdigest())
    return f'sha256sum={result}' if result else ''

#TODO: make sources replace the strings with a format strigns with pkgname and pkgver shit !!
result = f'''
# Generated with Cooker!
recipever=0
pkgname="{pkgname}"
pkgver="{pkgver}"
pkgdesc="{pkgdesc}"
url="{url}"
arch="x86_64"
license="{license}"
sources={sources}  
{generate_sha256(sources) if generate_hash else ""}
depends={depends}
makedepends={makedepends}
def build(c):
\tc.sh("{build_cmd}")
def install(c):
\tc.sh("{install_cmd}")
'''
with open(path, "w") as f:
    f.write(result)