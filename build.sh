#!/bin/bash
rm -rf dist/*
rm -rg build/*

python3 -m build . --wheel
