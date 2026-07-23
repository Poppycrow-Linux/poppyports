# About pbuild
Hello! This is meant to serve as a guide for contributors, people looking to make recipes, and people who want to understand the architecture of pbuild. Basically everything pbuild related goes here.
Please note our project is rapidly revolving and information you find here may be outdated/incorrect. As always, source code is the best documentation.

To put it simply, pbuild does one thing: build one package from one recipe. It is spiritually closer to something like alpine's [abuild](https://wiki.alpinelinux.org/wiki/Abuild_and_Helpers), with the benefit of it being written in python as opposed to an amalgamation of C and bash, and also uses python scripts as recipes as opposed to APKBUILDs.

## Recipes
Recipes are called recipes because they tell the computer how to "bake" the package.
I (Sam) designed them to be kind of similar to APKBUILDs so they're easier to grasp and also mechanically port from alpine's ports.
You can reuse some of the concepts from [APKBUILD's reference](https://wiki.alpinelinux.org/wiki/APKBUILD_Reference) to construct recipes.

The idea of using python recipes was borrowed from chimera's [cports](https://github.com/chimera-linux/cports), which have their own cbuild system.

Below, I describe the valid variables for recipes:

Please note this is not a final spec, and still under extensive development.

- `recipever`: Version of the recipe schema (still experimental, leave at 0)

- `pkgname`: Full name for the package. Passed to apkpkg and used to fetch sources from upstream.
- `pkgver`: Version of the software being packaged. Passed to apkpkg and used to fetch sources from upstream.
- `pkgrel`: Package release number, similar to APKBUILD pkgrel.
- `pkgdesc`: A brief description of the package and what it does. 
- `url`: The homepage for the package.
- `arch`: CPU architecture for the package to be built to, such as x86_64, aarch64, etc... Similar to APKBUILD arch.
- `license`: License used for the source code of the package.

- `sources`: List of remote source links to download and untar. We currently support HTTP and Git, but we would recommend using HTTP tarballs as they provide a stable checksum to compare against.
- `sha256sum`: List of sha256sums. Usually a 1:1 map between sources (i.e. sources[0] is checked against sha256sum[0]). Used for checking remote file integrity.
- `depends`: List of packages the recipe depends on at RUNTIME. (check apk runtime resolving)
- `makedepends`: list of packages the recipe depends on at BUILD-TIME. (TODO)

- `provides`: A list of "apps" the package provides, used to calculate conflicts. For example, if packages `foo` and `bar` both provide `baz`, they will conflict.

- `build(c)`: Compilation stage of the package. Both build prep and compiling happen here.
- `install(c)`: Installation/packaging stage of the package. This should install the final distributable files to `PKGDIR`.


Let's talk about the `c` variable, or `ctx`, or `BuildContext`.
The BuildContext provides the recipe with context regarding the environment it's running in, and functional/variable helpers for building packages.

Here's some of the variables you'll likely use. you can access them within `build` and `install` via the first argument:

- `PORTDIR`: Refers to the directory the port/recipe is in (like `main/apk/`)
- `SRCDIR`: Fefers to the directory where sources were installed and extracted (`pkgsrc`)
- `PKGDIR`: Fefers to the install directory whose files will be packaged into a `.apk` file (`pkgdir`)

- `ARCH`: Refers to the target system's architecture
- `CFLAGS/CXXFLAGS/LDFLAGS`: user defined(?) flags for C/C++/LD
- `NPROC`: Returns nproc from the system, or how many logical cores the system has.
- `LIBC`: Refers to our current libc (experimental, currently just `"glibc"`)
---

- `recipe`: Recursive reference to the current recipe
- `env`: Refers to the environment variables of the context, for things like `sh` and etc.

- `sh(*args, cwd=None)`: Run a command with args. If there is only one argument, it invokes the first one via the shell. If cwd = None, it defaults to `SRCDIR`.
- `apply_patches()`: Try to apply patches from `$PORTDIR/patches` inside of `SRCDIR`.
