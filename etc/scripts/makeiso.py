# I am very aware this is basically a bash script disguised as a python script. i didn't even test this. i have no idea if it works.
# its ok its staging
import os, subprocess

SIGNKEY = "crowapkteam-private.pem" # required!

print("Reading poppy-base dependencies")
recipe = {}
with open("main/poppy-base/recipe.py", "r") as f:
  exec(f.read(), recipe)

depends = ["main/poppy-base"] + recipe["depends"]
print(depends)


def sh(args, cwd=None):
  print(f"+$ {args}")
  subprocess.run(args, cwd=cwd, check=True, shell=True)

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
if os.path.exists("build/rootfs/"):
  sh("rm -rf build/rootfs/")


sh("mkdir -p build/rootfs/sys/fs/cgroup")
sh("mkdir -p build/rootfs/dev/pts")
sh("mkdir -p build/rootfs/dev/shm")
sh("mkdir -p build/rootfs/proc")
sh("mkdir -p build/rootfs/run")
sh("mkdir -p build/rootfs/usr/sbin")
sh("mkdir -p build/rootfs/usr/bin")
sh("mkdir -p build/rootfs/usr/lib")
FSDIR = os.getcwd() + "/build/rootfs/"
sh("ln -s usr/bin bin", cwd=FSDIR)
sh("ln -s usr/sbin sbin", cwd=FSDIR)
sh("ln -s usr/lib lib", cwd=FSDIR)
sh("ln -s usr/lib lib32", cwd=FSDIR)
sh("ln -s usr/lib lib64", cwd=FSDIR)
sh("ln -s lib lib32", cwd=FSDIR+"/usr")
sh("ln -s lib lib64", cwd=FSDIR+"/usr")
# hacky
sh("ln -s . ./x86_64-linux-gnu", cwd=FSDIR+"lib")

sh("mkdir -p build/rootfs/apks/x86_64/")

for dep in depends:
  print(f"building {dep}")
  sh(f"python3 pbuild.py -signkey {SIGNKEY} {dep} build/pkg/{dep}")
  sh(f"cp -v build/pkg/{dep}/*.apk build/rootfs/apks/x86_64/.")


print("generating apkindex...")
sh(f"apk --sign-key {SIGNKEY} mkndx --hash sha256 -o build/rootfs/apks/x86_64/Packages.adb build/rootfs/apks/x86_64/*.apk")

sh("apk add --allow-untrusted --initdb --root . ./apks/x86_64/*.apk", cwd=FSDIR)

print("generating initramfs")
#cd initramfs && (find . | cpio -o -H newc -R root:root > ../init.cpio) && cd ..
sh("find . | cpio -o -H newc -R root:root > ../init.cpio", cwd=FSDIR)


print("generating isoroot")
os.makedirs("build/isoroot/boot/grub/", exist_ok=True)

with open("build/isoroot/boot/grub/grub.cfg", 'w') as f:
  f.write("""set timeout=5
set default=0
menuentry "poppycrow" {
  linux /boot/bzImage
  initrd /boot/init.cpio
}""")

sh("cp -v build/rootfs/boot/bzImage build/isoroot/boot/bzImage")
sh("cp -v build/init.cpio           build/isoroot/boot/init.cpio")

sh("grub-mkrescue -o build/poppycrow.iso build/isoroot")
