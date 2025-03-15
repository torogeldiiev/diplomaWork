#!/bin/bash -eu
this_dir="$(readlink -f "$(dirname "$0")")"
cd "$this_dir"

rm -rf "$this_dir"/../server/venv
rm -rf "$this_dir"/../client/build
rm -rf "$this_dir"/../client/node_modules
