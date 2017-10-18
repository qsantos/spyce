Description
-----------

This directory contains C code that can be used by Spyce for faster execution
once compiled as program extensions (`*.so` or `*.dll`).

Dependencies
------------

`gcc make pkg-config python3-dev`

Compile
-------

To compile, run:

```shell
$ make
gcc -std=c99 -Wall -Wextra -Werror -pedantic -O3 -I /usr/include/python3.4 -shared -fPIC orbit_ext.c -o orbit.so
```
