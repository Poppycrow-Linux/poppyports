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
print("Type in build commands. Press ENTER after each one and type in END as the last command to end it:\n")
build_cmds = []
while True:
    i = input("")
    if i.lower() == "end":
        break
    build_cmds.append(i)
print("Type in install commands. Press ENTER after each one and type in END as the last command to end it::")
install_cmds = []
while True:
    i = input("")
    if i.lower() == "end":
        break
    install_cmds.append(i)
print()
category = input("Package Category:")[0].lower() == "y"
directory = pathlib.Path(category) / pkgname
directory.mkdir(parents=True,exist_ok=True)
path = directory / "recipe.py"
#FIXME: fix this. outputs wrong output 
def generate_sha256(sources):
    result = []
    for s in sources:
        response = requests.get(url)
        result.append(hashlib.sha256(response.content).hexdigest())
    return f'sha256sum={result}' if result else ''
source_line = '['
for s in sources:
    source_line += f'f"{s.replace(pkgname, '{pkgname}').replace(pkgver, '{pkgver}')}"'
source_line += ']'
build_lines = "\n".join(f'\tc.sh("{cmd}")' for cmd in build_cmds)
install_lines = "\n".join(f'\tc.sh("{cmd}")' for cmd in install_cmds)
result = f'''# Generated with Cooker!
recipever=0
pkgname="{pkgname}"
pkgver="{pkgver}"
pkgdesc="{pkgdesc}"
url="{url}"
arch="x86_64"
license="{license}"
sources={source_line}  
{generate_sha256(sources) if generate_hash else ""}
depends={depends}
makedepends={makedepends}
def build(c):
{build_lines}
def install(c):
{install_lines}
'''
with open(path, "w") as f:
    f.write(result)