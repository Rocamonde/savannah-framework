#!/usr/bin/env bash

python ptestl.py

while read p; do
  python "$p"
done < .testl

rm .testl