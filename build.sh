#!/bin/bash
rm -rf dist/*
pip -m build . --wheel
