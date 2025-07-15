#!/bin/bash
rm -rf dist/*
rm -rf build/*

python3.12 -m build --wheel

