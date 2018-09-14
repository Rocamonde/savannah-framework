#!/usr/bin/env bash

for file in *
do
  python "tests/$file"
done