import argparse
import os
import sys
import shutil
import subprocess

env = os.environ.copy()

class Colors:
    ERROR = "\x1b[5;97;101m"
    WARNING = "\x1b[5;30;103m"
    SUCCESS = "\x1b[0;97;48;5;28m"
    SH_COMMAND = "\x1b[0;97;48;5;21m"
    END = "\x1b[0m"
    UNPACKAGED = "\x1b[30;43m"


def log(color, *args):
    print(f"{color or ''}I:", *args, Colors.END)

def sh(*args, cwd=None, shell=False):
    if cwd is None: cwd = os.getcwd()
    if len(args) == 1: shell = True

    # shell=True requires a string to be passed in i assume
    cmd = " ".join(args) if shell else args

    log(Colors.SH_COMMAND, f"+$ {' '.join(args) if isinstance(cmd, tuple) else cmd}")
    subprocess.run(cmd, cwd=cwd, env=env, check=True, shell=shell)

parser = argparse.ArgumentParser(
    prog="makeisoworse_realiso",
    # suggest_on_error=True, # this doesn't work on my python 3.13
    description="Makes the rootfs and an init.cpio, then turns it into an iso",
    epilog="See more @ https://codeberg.org/Poppycrow-Linux/poppyports",
)

parser.add_argument("-force", "-force-rebuild", "-fr", "-fresh", action="store_true", help="Deletes the rootfs before building.")

args = parser.parse_args()
force = args.force

print("checking for xorriso...")
if shutil.which("xorriso") is None:
    print("xorriso is REQUIRED to be in path.")
    sys.exit(1)

print("Reading livecd-base dependencies")
recipe = {}
with open("recipes/main/livecd-base/recipe.py", "r") as f:
  exec(f.read(), recipe)

depends = ["main/livecd-base"] + recipe["depends"]
print(depends)

# set up rootfs
"""
/sbin links to /usr/sbin
/usr/sbin links to /bin which then links to /usr/bin
/bin links to /usr/bin
/lib links to /usr/lib
/lib32 links to /usr/lib32
/lib64 links to /usr/lib64
/dev
/dev/pts
/dev/shm
/sys
/sys/fs/cgroup
/proc
/boot is a part of livecd-base because i put the limine config here like a lazy CHUD
"""

if os.path.exists("build/rootfs"):
    if not(force):
        print("rootfs already exists. delete it before running this")
        exit(1)
    else:
        print("Force flag was passed, nuking the rootfs dir!")
        shutil.rmtree("build/rootfs")



subprocess.run(("mkdir","-p","build/rootfs/sys/fs/cgroup"))
subprocess.run(("mkdir","-p","build/rootfs/dev/pts"))
subprocess.run(("mkdir","-p","build/rootfs/dev/shm"))
subprocess.run(("mkdir","-p","build/rootfs/proc"))
subprocess.run(("mkdir","-p","build/rootfs/run"))
subprocess.run(("mkdir","-p","build/rootfs/boot"))
subprocess.run(("mkdir","-p","build/rootfs/usr/bin"))
subprocess.run(("mkdir","-p","build/rootfs/usr/lib"))
subprocess.run(("ln", "-s", "usr/bin", "bin"), cwd= os.getcwd()+"/build/rootfs")
subprocess.run(("ln", "-s", "usr/bin", "sbin"), cwd= os.getcwd()+"/build/rootfs")
subprocess.run(("ln", "-s", "bin", "sbin"), cwd=os.getcwd()+"/build/rootfs/usr")
subprocess.run(("ln","-s","usr/lib","lib"),cwd=os.getcwd()+"/build/rootfs")
#subprocess.run(("ln","-s","usr/lib","lib32"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","usr/lib","lib64"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","lib","lib64"),cwd=os.getcwd()+"/build/rootfs/usr")
#subprocess.run(("ln","-s","lib","lib32"),cwd=os.getcwd()+"/build/rootfs/usr")
subprocess.run(("ln","-s",".","./x86_64-linux-gnu"),cwd=os.getcwd()+"/build/rootfs/lib") # ugly hack
subprocess.run(("rsync","-r","-v","recipes/main/poppy-base/overlay/.","build/rootfs/"))


for dep in depends:
  print(f"building {dep}")
  subprocess.run(["python3", "pbuild", f"{dep}", f"build/pkg/{dep}"])
  print(f"Copying the contents of build/pkg/{dep}/pkgdir/ to build/rootfs/")
  subprocess.run(["rsync", "-r", "-l", "-K", "-H", f"build/pkg/{dep}/pkgdir/.", "build/rootfs/"])


# TODO: print(f"generating apkindex")
#       do this in build/repo/APKINDEX.tar.gz
#       oh also copy all the apks there.


print("generating initramfs")
#cd initramfs && (find . | cpio -o -H newc -R root:root > ../init.cpio) && cd ..
subprocess.run("find . | cpio -o -H newc -R root:root > ../init.cpio", cwd="build/rootfs/", shell=True)

os.makedirs("build/isoroot/boot/", exist_ok=True)

#subprocess.run(["cp", "-v", "build/rootfs/boot/bzImage", "build/isoroot/boot/bzImage"])
# commented the line above out because why don't we just make the rootfs into the iso??

print("time to iso!")
bootloader = "limine"
log(Colors.SH_COMMAND,f"compiling {bootloader}")
subprocess.run(["python3", "pbuild", f"main/{bootloader}", f"build/pkg/{bootloader}"], check = False) # all bootloaders are in main repo i think?
match bootloader: #WARNING: extreme jank ahead!
    case "limine":
        liminedir = f"build/pkg/{bootloader}/pkgdir"
        sh(f"cp {liminedir}/usr/local/share/limine/* build/rootfs/boot/", shell = True)
        cmd = "xorriso -as mkisofs -R -r -J -b boot/limine-bios-cd.bin \
                -no-emul-boot -boot-load-size 4 -boot-info-table -hfsplus \
                -apm-block-size 2048 --efi-boot boot/limine-uefi-cd.bin \
                -efi-boot-part --efi-boot-image --protective-msdos-label \
                . -o image.iso"
        sh(cmd, cwd = "build/rootfs")
        sh(f"{os.getcwd()}/{liminedir}/usr/local/bin/limine bios-install image.iso",  cwd = os.getcwd() + "/build/rootfs")
