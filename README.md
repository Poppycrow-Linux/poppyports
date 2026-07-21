## What is this repo?
This is the ports repository for [Poppycrow Linux](https://github.com/Poppycrow-Linux).
Check [staging branch](https://github.com/Poppycrow-Linux/poppyports/tree/staging) for staging stuff

## Usage
usage: pbuild [-h] [-ignoreintegrity] [-fresh] pkgpath builddir

Compiles apk files to be used in Poppycrow Linux repos.
```
positional arguments:
  pkgpath               Path of the folder that contains the build recipe.
  builddir              The directory to build the recipe in.

options:
  -h, --help            show this help message and exit
  -ignoreintegrity, -ii, -ignore-broken-files
                        Ignore any checksum errors and continue building the package.
  -fresh, -new, -redownload
                        Redownload files even if they are already present and pass the
                        integrity checks.
  -rebuild
                        Rebuilds even the packages that were previously compiled.
```

##  What is ports?
Ports is a repository of a packages you (or Github Actions) build. Think AUR or [cports](https://github.com/chimera-linux/cports) (shoutout to chimera linux they are awesome). 

##  Can I add software [xyz] to ports?
Not right now, the ports system is far from being finished.

## TODO
- [X] Make a super basic python script
- [ ] Add makedeps check and makedeps in general
- [ ] Make a more elaborate compiling system
- [ ] Sandbox the compiling process maybe??
- [ ] Manage a temporary apk repo
- [ ] Make the system be able to work with Github Actions and also forward things to our own server so we can actually host things.

## Subtitles?
subtitles by DimaTorzok
