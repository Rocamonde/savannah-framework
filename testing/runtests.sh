#!/usr/bin/env bash

python ptestl.py

while read p; do
  coverage run "$p"
done < .testl

rm .testl