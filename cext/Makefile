CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Werror -pedantic -O3
TARGETS = elements.so elements_py2.so elements_py3.so

all: $(TARGETS)

elements.so: elements.c
	$(CC) $(CFLAGS) -shared -fPIC $< -o $@

elements_py2.so: elements_ext.c elements.c
	$(CC) $(CFLAGS) -I /usr/include/python2.7 -shared -fPIC $< -o $@

elements_py3.so: elements_ext.c elements.c
	$(CC) $(CFLAGS) -I /usr/include/python3.4 -shared -fPIC $< -o $@

destroy:
	rm -f $(TARGETS)

rebuild: destroy all
