#!/usr/bin/env bash

python -m unittest discover -s tests/
coverage run --source=../savannah -m unittest discover -s tests/
coverage report -m