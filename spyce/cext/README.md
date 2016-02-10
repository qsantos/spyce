Description
-----------

This directory contains C code that can be used by Spyce for faster execution
once compiled as program extensions (`*.so` or `*.dll`).

Dependencies
------------

For:

* Python 2.x: `gcc make pkg-config python-dev`
* Python 3.x: `gcc make pkg-config python3-dev`

Compile
-------

To compile, run:

```shell
$ make
gcc -std=c99 -Wall -Wextra -Werror -pedantic -O3 -shared -fPIC elements.c -o elements.so
gcc -std=c99 -Wall -Wextra -Werror -pedantic -O3 -I /usr/include/python2.7 -shared -fPIC elements_ext.c -o elements_py2.so
gcc -std=c99 -Wall -Wextra -Werror -pedantic -O3 -I /usr/include/python3.4 -shared -fPIC elements_ext.c -o elements_py3.so
```

Reset
-----

To remove the compiled program extensions, run:

```shell
$ make destroy
```
