# On SBUs


## Introduction

The Poppycrow Ports system uses SBUs (Standard Build Units) for users to estimate build time, a system adapted from the [Linux from Scratch](https://www.linuxfromscratch.org/~bdubbs/about.html) project.
SBUs are heavily recommended to be added by maintainers as we use them to estimate the best CI server to send the build job to. For information on how to do this, see the guide on writing ports.
These units are a floating point integer with one decimal point of precision (for example, 3.1).

## How to calculate 1 SBU for a given system

One SBU is defined as the time it takes to configure and install the ncurses library on one core (which means NO multithreading). 
Since build time varies severely from computer to computer, the calculated SBU time is only applicable to that specific computer, and is invalidated by upgrades of any kind.
In order to time this, a user may run the following bash script in the build directory:

```
time {
	./configure --enable-widec --with-shared --without-normal --without-debug --with-termlib &&
	make;
}
```

When the build finishes, it will print three numbers, `real`, `user`, and `sys`. Only `real` is relevant, and that is the time of 1 SBU. 
You can use this time value to calculate the approximate time a package will take to build. For instance, if package foo has 3.2 SBUs, and your calculated
SBU is 1 minute, multiply 1 minute by 3.2 to get 3 minutes 12 seconds.


## How to calculate the SBU for a newly added recipe 

First, you must procure your system's SBU value from the section above. Then, time the compile of (but NOT THE INSTALL) your package from source (singlethreadedly, -j1 with Make) as the recipe specifies.
Divide this time by your SBU time. For instance, if your SBU is 2 minutes and the package takes 30 minutes to compile, divide 30 by 2 to get 15, so the SBU value is 15.0.
