#!/bin/bash
cd $(dirname $0)

cd spyce/

echo "Running test for python2"
if which python2-coverage 2>&1 >/dev/null
then
    python2-coverage run --source . -m unittest discover
    python2-coverage report
else
    python2 -m unittest discover
fi

echo "Running test for python3"
if which python3-coverage 2>&1 >/dev/null
then
    python3-coverage run --source . -m unittest discover
    python3-coverage report
else
    python3 -m unittest discover
fi

cd ..

echo "Checking compliance with PEP 8"
git ls-files -z | grep -z '\.py$' | xargs -0 pep8
