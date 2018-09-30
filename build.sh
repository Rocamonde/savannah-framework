#!/usr/bin/env bash

# Install package
python setup.py install

# Change directory to tests
cd tests/

# Run tests
for file in *
do
  python "$file"
done