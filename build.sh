#!/usr/bin/env bash

# Install package
python setup.py install

# Run tests
cd testing/tests
pytest --cov=./

# Implement code coverage
codecov --token="3e7d4a10-3e11-4137-8221-38a7fc7a2bf2"
