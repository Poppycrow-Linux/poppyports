# about pbuild
hello! this is meant to serve as a guide for contributors, people looking to make recipes, and people who want to understand the architecture of pbuild. basically everything pbuild related goes here.
please note our project is rapidly revolving and information you find here may be outdated/incorrect. as always, source code is the best documentation.

to put it simply, pbuild does one thing: build one package from one recipe. it is spiritually closer to something like alpine's [abuild](https://wiki.alpinelinux.org/wiki/Abuild_and_Helpers), with the benefit of it being written in python as opposed to a amalgamation of C and bash, and also uses python scripts as recipes as opposed to APKBUILDs.

## recipes
recipes are called recipes because they tell the computer how to "bake" the package.
i (sam) designed them to be kind of similar to APKBUILDs so they're easier to grasp and also mechanically port from alpine's ports.
you can reuse some of the concepts from [APKBUILD's reference](https://wiki.alpinelinux.org/wiki/APKBUILD_Reference) to construct recipes.

the idea of using python recipes was borrowed from chimera's [cports](https://github.com/chimera-linux/cports), which have their own cbuild system.


below, i describe the valid variables for recipes:

please note this is not a final spec and is rapidly changing

- `recipever`: recipe version (? this is experimental)

- `pkgname`: full name for the package, used in apk when constructing and repos (via apk mkpkg and such).
- `pkgver`: version of the software being packaged (passed in to apk package as well)
- `pkgrel`: package release number. similar to APKBUILD pkgrel
- `pkgdesc`: brief package description
- `url`: homepage for the package
- `arch`: package architecture to build for (x86, x86_64, all, noarch)... similar to APKBUILD arch
- `license`: distribution license of the package

- `sources`: list of remote source links to download and untar. we currently support HTTP and git, but i would recommend using http tarballs as they provide a stable checksum to compare against.
- `sha256sum`: list of sha256sums. usually a 1:1 map between sources (i.e. sources[0] is checked against sha256sum[0]), is used for checking remote file integrity.
- `depends`: list of packages the recipe depends on for RUN-TIME (check apk runtime resolving)
- `makedepends`: list of packages the recipe depends on BUILD-TIME (TODO)

- `provides`: list of package names (or files?) this package provides (check APKBUILD provides) (TODO)

- `build(c)`: compilation stage of the package. Both build prep and compiling happen here.
- `install(c)`: installation/packaging stage of the package. This should install the final distributable files to `PKGDIR`.


let's talk about the `c` variable, or `ctx`, or `BuildContext`.
the BuildContext provides the recipe with context regarding the environment it's running in, and functional/variable helpers for building packages.

here's some of the variables you'll likely use. you can access them within `build` and `install` via the first argument:

- `PORTDIR`: refers to the directory the port/recipe is in (like `main/apk/`)
- `SRCDIR`: refers to the directory where sources were installed and extracted (`pkgsrc`)
- `PKGDIR`: refers to the install directory whose files will be packaged into a `.apk` file (`pkgdir`)

- `ARCH`: refers to the target systems architecture
- `CFLAGS/CXXFLAGS/LDFLAGS`: user defined(?) flags for C/C++/LD
- `NPROC`: get available os core count
- `LIBC`: refers to our current libc (experimental, currently just `"glibc"`)
---

- `recipe`: circular reference to the current recipe
- `env`: refers to the environment variables of the context, for things like `sh` and etc.

- `sh(*args, cwd=None)`: runs a command with args. if there is only one argument, it invokes the first one via the shell. if cwd=None, it defaults to `SRCDIR`.
- `apply_patches()`: tries to apply patches from `$PORTDIR/patches` inside of `SRCDIR`
