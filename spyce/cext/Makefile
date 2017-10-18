CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Werror -O3
TARGETS = orbit.so

all: $(TARGETS)

%.so: %_ext.c %.c
	$(CC) $(CFLAGS) $$(pkg-config --cflags python3) -shared -fPIC $< -o $@

destroy:
	rm -f $(TARGETS)

rebuild: destroy all
