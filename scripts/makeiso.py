# I am very aware this is basically a bash script disguised as a python script. i didn't even test this. i have no idea if it works.
# its ok its staging
import os, subprocess

print("Reading poppy-base dependencies")
recipe = {}
with open("main/poppy-base/recipe.py", "r") as f:
  exec(f.read(), recipe)

depends = recipe["depends"] + ["poppy-base"]
print(depends)

for dep in depends:
  print(f"building {dep}")
  subprocess.run(["python3", "pbuild.py", f"main/{dep}", f"build/pkg/{dep}"])
  subprocess.run(["cp", "-a", f"build/pkg/{dep}/pkgdir/.", "build/rootfs/"])

# TODO: print(f"generating apkindex")
#       do this in build/repo/APKINDEX.tar.gz
#       oh also copy all the apks there.


print("generating initramfs")
#cd initramfs && (find . | cpio -o -H newc -R root:root > ../init.cpio) && cd ..
subprocess.run("find . | cpio -o -H newc -R root:root > ../init.cpio", cwd="build/rootfs/", shell=True)


print("generating isoroot")
os.makedirs("build/isoroot/boot/grub/", exist_ok=True)

with open("build/isoroot/boot/grub/grub.cfg", 'w') as f:
  f.write("""set timeout=5
set default=0
menuentry "poppycrow" {
  linux /boot/bzImage
  initrd /boot/init.cpio
}""")

subprocess.run(["cp", "-v", "build/rootfs/boot/bzImage", "build/isoroot/boot/bzImage"])  
subprocess.run(["cp", "-v", "build/init.cpio", "build/isoroot/boot/init.cpio"])

subprocess.run(["grub-mkrescue", "-o", "build/poppycrow.iso", "build/isoroot"])
