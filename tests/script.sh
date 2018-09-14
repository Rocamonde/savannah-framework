#!/usr/bin/env bash

for file in tests/*
do
  python "$file"
done