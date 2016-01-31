CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Werror -O3
TARGETS = orbit.so orbit_py2.so orbit_py3.so

all: $(TARGETS)

%.so: %.c
	$(CC) $(CFLAGS) -shared -fPIC $< -o $@

%_py2.so: %_ext.c %.c
	$(CC) $(CFLAGS) $$(pkg-config --cflags python2) -shared -fPIC $< -o $@

%_py3.so: %_ext.c %.c
	$(CC) $(CFLAGS) $$(pkg-config --cflags python3) -shared -fPIC $< -o $@

destroy:
	rm -f $(TARGETS)

rebuild: destroy all
