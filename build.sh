#!/bin/bash
rm -rf dist/*
python3 -m build . --wheel
