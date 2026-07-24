# TODO: smartly skip which pkgs are compiled and didnt change
# TODO: figure out how to integrate repo with apk
import os, subprocess

ARCH = "x86_64"
REPOS = ["main", "extra"]


def sh(args, cwd=None):
  print(f"+$ {args}")
  subprocess.run(args, cwd=cwd, check=True, shell=True)

sh(f"mkdir -p build/apks/{ARCH}/")

done, fail = 0, 0
for repo in REPOS:
  print(f"CI Building repo {repo}")
  pkgs = sorted(os.listdir(repo))
  for pkg in pkgs:
    print(f"CI Building {repo}:{pkg}")
    try:
      sh(f"python3 pbuild.py {repo}/{pkg} build/pkg/{repo}/{pkg}")
      sh(f"cp -v build/pkg/{repo}/{pkg}/*.apk build/apks/{ARCH}/.")
      done += 1
    except Exception as e:
      print(f"ERROR during building {pkg}: {e}\n")
      fail += 1; done += 1


print(f"CI summary: {done} done, {fail} failed, {done-fail} success")

# https://man.archlinux.org/man/apk-mkndx.8.en
# https://man.archlinux.org/man/apk-repositories.5.en   "index (v3) is at $base_url/$arch/Packages.adb"  "default package path: $base_url/$arch/$name-$version.apk"
print("generating apkindex...")
sh(f"apk mkndx --hash sha256 -o build/apks/{ARCH}/Packages.adb build/apks/{ARCH}/*.apk")
