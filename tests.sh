#!/bin/bash
set -e
cd $(dirname $0)

cd spyce/

echo "Running test for python2"
python2-coverage run --source . -m unittest discover
python2-coverage report

echo "Running test for python3"
python3-coverage run --source . -m unittest discover
python3-coverage report

cd ..

echo "Checking compliance with PEP 8"
git ls-tree -rz --name-only HEAD | grep -z '\.py$' | xargs -0 pep8
