#!/bin/bash
set -e
rm -rf venv
python3 -m venv venv
. venv/bin/activate
pip install -e .