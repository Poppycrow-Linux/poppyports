import argparse
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(
    prog="makeisoworse",
    # suggest_on_error=True, # this doesn't work on my python 3.13
    description="Makes the rootfs and an init.cpio.",
    epilog="See more @ https://codeberg.org/Poppycrow-Linux/poppyports",
)

parser.add_argument("-force", "-force-rebuild", "-fr", "-fresh", action="store_true", help="Deletes the rootfs before building.")

args = parser.parse_args()
force = args.force

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
  subprocess.run(["python3", "pbuild.py", f"{dep}", f"build/pkg/{dep}"])
  subprocess.run(["rsync", "-r", "-l", "-K", "-H", f"build/pkg/{dep}/pkgdir/.", "build/rootfs/"])

# TODO: print(f"generating apkindex")
#       do this in build/repo/APKINDEX.tar.gz
#       oh also copy all the apks there.


print("generating initramfs")
#cd initramfs && (find . | cpio -o -H newc -R root:root > ../init.cpio) && cd ..
subprocess.run("find . | cpio -o -H newc -R root:root > ../init.cpio", cwd="build/rootfs/", shell=True)

os.makedirs("build/isoroot/boot/", exist_ok=True)

subprocess.run(["cp", "-v", "build/rootfs/boot/bzImage", "build/isoroot/boot/bzImage"])
