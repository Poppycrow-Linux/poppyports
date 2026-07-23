import os, subprocess

print("Reading poppy-base dependencies")
recipe = {}
with open("main/poppy-base/recipe.py", "r") as f:
  exec(f.read(), recipe)

depends = ["main/poppy-base"] + recipe["depends"]
print(depends)

# set up rootfs
"""
/sbin links to /usr/sbin
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
  print("rootfs already exists. delete it before running this")
  exit(1)

subprocess.run(("mkdir","-p","build/rootfs/sys/fs/cgroup"))
subprocess.run(("mkdir","-p","build/rootfs/dev/pts"))
subprocess.run(("mkdir","-p","build/rootfs/dev/shm"))
subprocess.run(("mkdir","-p","build/rootfs/proc"))
subprocess.run(("mkdir","-p","build/rootfs/run"))
subprocess.run(("mkdir","-p","build/rootfs/usr/sbin"))
subprocess.run(("mkdir","-p","build/rootfs/usr/bin"))
subprocess.run(("mkdir","-p","build/rootfs/usr/lib"))
subprocess.run(("ln","-s","usr/bin","bin"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","usr/sbin","sbin"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","usr/lib","lib"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","usr/lib","lib32"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","usr/lib","lib64"),cwd=os.getcwd()+"/build/rootfs")
subprocess.run(("ln","-s","lib","lib64"),cwd=os.getcwd()+"/build/rootfs/usr")
subprocess.run(("ln","-s","lib","lib32"),cwd=os.getcwd()+"/build/rootfs/usr")
subprocess.run(("ln","-s",".","./x86_64-linux-gnu"),cwd=os.getcwd()+"/build/rootfs/lib")
subprocess.run(("rsync","-r","-v","main/poppy-base/overlay/.","build/rootfs/"))


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
