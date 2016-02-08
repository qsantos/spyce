#!/usr/bin/python3
"""Check version of OpenGL functions in source files"""

import re
import os
import sys
import itertools
import collections

# parse arguments
try:
    rootdir = sys.argv[1]
except IndexError:
    rootdir = '.'

# list OpenGL functions used in source files
used_gl_functions = set()
for path, _, filenames in os.walk(rootdir):
    for filename in filenames:
        # filter source files
        _, _, ext = filename.rpartition('.')
        if ext not in ('py', 'c', 'cpp', 'cs'):
            continue
        # find all names looking like OpenGL functions
        with open(os.path.join(path, filename)) as f:
            used_gl_functions |= set(re.findall(r'gl[A-Z]\w+', f.read()))

# locate and read gl.spec file
# source https://www.opengl.org/registry/oldspecs/gl.spec
spec_path = os.path.join(os.path.dirname(__file__), 'gl.spec')
with open(spec_path) as f:
    spec = f.read()

# parse specification
versions = collections.defaultdict(lambda: "unknown")
deprecated = set()
for match in re.finditer(r'(?m)^([A-Z]\w*)\(.*(?:\n^.+)*', spec):
    function_name = 'gl' + match.group(1)
    version = re.search(r'(?m)^\tversion\s*(.+)$', match.group())
    if version is None:
        continue
    versions[function_name] = version.group(1)
    if 'deprecated' in match.group():
        deprecated.add(function_name)

# display functions grouped by version
sorted_functions = sorted(used_gl_functions, key=versions.__getitem__)
grouped_by_version = itertools.groupby(sorted_functions, versions.__getitem__)
for version, functions in grouped_by_version:
    print('# OpenGL %s' % version)
    print()
    for function in sorted(functions):
        print('* %s' % function)
    print()

# display deprecated functions
print('# Deprecated')
print()
for function in sorted(used_gl_functions & deprecated):
    print('* %s' % function)
