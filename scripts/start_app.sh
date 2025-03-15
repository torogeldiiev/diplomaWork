#!/bin/bash -eu

# Get the directory of the script
this_dir="$(readlink -f "$(dirname "$0")")"

# Load environment variables
config="${1:-}"
if [ -z "$config" ]; then
  echo "Usage: $0 <config-file>"
  exit 1
fi

if [ -e "$config" ]; then
  config="$(readlink -f "$config")"
fi

cd "$this_dir"/../server
source venv/bin/activate

echo "Starting Flask application..."
ENV_FILE="$config" flask run
