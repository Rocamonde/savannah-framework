#!/usr/bin/env bash

# Install package
python setup.py install

# Run tests
for file in tests/*
do
  python "$file"
done