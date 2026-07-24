#  Poppycrow Linux Ports

## Important!!!
[Codeberg](https://codeberg.org/Poppycrow-Linux/poppyports) is the main repo for poppyports. Any issues or pull requests should be submitted there instead of the mirrors (Github, etc)

### What is this repo?
This is the ports repository for [Poppycrow Linux](https://codeberg.org/Poppycrow-Linux).

###  What are ports?
Ports is a repository of a packages you (or a CI server) build, with optional configuration changes and patches applied beforehand. This system is directly inspired
from the ports system found on FreeBSD and OpenBSD, but inspiration for our incarnation of the system was largely taken from [Chimera Linux](https://chimera-linux.org/)'s cports.

###  Can I add software [xyz] to ports?
Not right now, the ports system is far from being finished.

## The build system

Our build system, pbuild, sources packages directly from their upstream, verifies their SHA signature, and then builds them into an APK package.
Optionally, the user may also supply patches that are then applied onto the extracted sources before they are compiled. Some packages, such as extra/figlet,
come with their own Poppycrow provided patches that provide distro-specific features and support.  

### Usage
```
usage: pbuild [-h] [-ignoreintegrity [IGNOREINTEGRITY]] [-fresh [FRESH]] [-rebuild [REBUILD]] [-color [COLOR]] [-supressnonerrorlogs [SUPRESSNONERRORLOGS]] [-config [CONFIG]] pkgpath [builddir]

Compiles apk files to be used in Poppycrow Linux repos.

positional arguments:
  pkgpath               Path of the folder that contains the build recipe.
  builddir              The directory to build the recipe in.

options:
  -h, --help            show this help message and exit
  -ignoreintegrity, -ii, -ignore-broken-files [true/false]
                        Ignore any checksum errors and continue building the package.
  -fresh, -new, -redownload [true/false]
                        Redownload files even if they are already present and pass the integrity checks.
  -rebuild [true/false]    Force rebuild even when package is already built.
  -color [true/false]        Highlight warnings, errors and build completion.
  -supressnonerrorlogs, -clean-logs [true/false]
                        Supress logs that aren't warnings, errors, or completion messages
  -config [PATH]      The config to use.
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


## Subtitles?
subtitles by DimaTorzok
