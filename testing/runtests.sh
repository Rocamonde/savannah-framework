#!/usr/bin/env bash

while read p; do
  python "$p"
done < testing/.testl