#!/usr/bin/env bash

# Install package
python setup.py install

# Run tests
cd testing
sh runtests.sh