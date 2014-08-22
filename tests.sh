#!/bin/bash
set -e

echo "Running test for python2"
python2 tests.py

echo "Running test for python3"
python3 tests.py
