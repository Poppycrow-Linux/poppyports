# Poppycrow Linux Ports

## Important!!!
[Codeberg](https://codeberg.org/Poppycrow-Linux/poppyports) is the main repo for poppyports. Any issues or pull requests should be submitted there instead of the mirrors (Github, etc)

### What is this repo?
This is the ports repository for [Poppycrow Linux](https://codeberg.org/Poppycrow-Linux).

###  What are ports?
Ports is a repository of a packages you (or a CI server) build, with optional configuration changes and patches applied beforehand. This system is directly inspired
from the ports system found on FreeBSD and OpenBSD, but inspiration for our incarnation of the system was largely taken from [Chimera Linux](https://chimera-linux.org/)'s cports.

###  Can I add software [xyz] to ports?
While the port system is unfinished, the spec right now is good enough to mitigate breaking changes when they appear. Read CONTRIBUTING.md, and also the docs in the `etc/docs` folder to know the recipe spec. Once you get your recipe to build, feel free to open a PR. If things really do work, and especially if the package is in the high priority issues list, it's probably going to be accepted. 

## What software to package?
The system, as it is right now, boots. And that's about it. We lack networking, graphics, the init system doesn't really work, so any package that helps with that is very welcome. If you don't want to package anything from issues, you can run the 'whattopackage.py' script, which looks for any unpackaged dependencies of things that are already packaged. 

## The build system

Our build system, pbuild, sources packages directly from their upstream, verifies their SHA signature, and then builds them into an APK package.
Optionally, the user may also supply patches that are then applied onto the extracted sources before they are compiled. Some packages, such as extra/figlet,
come with their own Poppycrow provided patches that provide distro-specific features and support.  

### Usage
```
usage: pbuild [-h] [-ignoreintegrity [IGNOREINTEGRITY]] [-fresh [FRESH]] [-rebuild [REBUILD]] [-color [COLOR]] [-buildstatebreakdown [BUILDSTATEBREAKDOWN]] [-supressnonerrorlogs [SUPRESSNONERRORLOGS]]
              [-config [CONFIG]] [-portsdir [PORTSDIR]] [-appendportsdirtopath [APPENDPORTSDIRTOPATH]] [-signkey [SIGNKEY]]
              pkgpath [builddir]

Compiles apk files to be used in Poppycrow Linux repos.

positional arguments:
  pkgpath               Path of the folder that contains the build recipe.
  builddir              The directory to build the recipe in.

options:
  -h, --help            show this help message and exit
  -ignoreintegrity, -ii, -ignore-broken-files [IGNOREINTEGRITY]
                        Ignore any checksum errors and continue building the package.
  -fresh, -new, -redownload [FRESH]
                        Redownload files even if they are already present and pass the integrity checks.
  -rebuild [REBUILD]    Force rebuild even when package is already built.
  -color [COLOR]        Highlight warnings, errors and build completion.
  -buildstatebreakdown, -bsbd, -bb [BUILDSTATEBREAKDOWN]
                        Show build state breakdown.
  -supressnonerrorlogs, -clean-logs [SUPRESSNONERRORLOGS]
                        Supress logs that aren't warnings, errors, or completion messages
  -config [CONFIG]      The config to use.
  -portsdir [PORTSDIR]  Folder with ports in it.
  -appendportsdirtopath, -apd [APPENDPORTSDIRTOPATH]
                        Appends the ports directory to the path of the recipe to build. Defaults to true, so syntax like pbuild main/linux-stable continues to work.
  -signkey [SIGNKEY]    Signature private key to use for apk signing

See more @ https://codeberg.org/Poppycrow-Linux/poppyports
```


## TODO
- [ ] Add makedeps check and makedeps in general
- [ ] Make a more elaborate compiling system
- [ ] Sandbox the compiling process maybe??
- [ ] Manage a temporary apk repo
- [ ] Make the system be able to work with Github Actions and also forward things to our own server so we can actually host things.

## Building the kernel with rootfs
We provide our own build script for a patched kernel with a rootfs image:

`python3 scripts/makeisoworse.py`

(Please note, in this early development stage, this script does not build a bootable ISO. You must boot it with qemu-system manually.)

## How do I boot and test my packages?
Right now you run the `etc/scripts/makeisoworse.py` script. If you want a specific package to be rebuit as part of the makeisoworse process, just delete its respective folder from build/pkg. After the process finishes, you gain the aforementioned build/pkg directory, along with isoroot, which is currently only used to output the bzImage, and the rootfs directory. To run the system that's just been built with makeisoworse, while inside the build directory run the following command:
`qemu-system-x86_64 -kernel ./isoroot/boot/bzImage -initrd init.cpio -m 8G -append "console=ttyS0" -nographic`
While running things in the nographic mode is far from necessary, this allows us to print dinit states and whatnot while it appears to "hang".
For even more information on how the system is built, you can inspect the makeisoworse script itself, livecd-base and base-poppy recipes.
Do note, that as of now, you need to enable agetty and udevd manually before exiting to dinit and continuing to boot, otherwise you might get seemingly stuck on local.target. 


## Subtitles?
subtitles by DimaTorzok
