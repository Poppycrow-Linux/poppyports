## what do the scripts do???
it's mostly self explanatory, but some of them need clarification

`makeisoworse.py` - makes a rootfs and a kernel you can use to boot things in qemu
`makesysroot.py` - does not actually make a sysroot. just makes a very stripped down rootfs you can chroot (or bwrap) into
`build_toolchain.sh` - makes an actual sysroot. example: `ARCH=x86_64 LIBC=glibc VENDOR=crow ./build_toolchain.sh`. This builds a toolchain for a triplet of `x86_64-crow-linux-gnu`
