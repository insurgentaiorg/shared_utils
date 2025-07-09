#!/bin/bash
rm -rf dist/*
rm -rf build/*

python3 -m build . --wheel
