#!/bin/bash -eu

# Get the directory of the script
this_dir="$(readlink -f "$(dirname "$0")")"

# Load environment variables if provided
if [ $# -ne 0 ]; then
  config="$1"
  source "$config"
fi

# Setup the server environment
cd "$this_dir"/../server
if [ ! -d venv ]; then
  python3 -m venv venv
  source venv/bin/activate
  python3 -m pip install --upgrade pip
else
  source venv/bin/activate
fi

python3 -m pip install -r requirements.txt

# Setup the client (React app)
cd "$this_dir"/../client

# Check if package.json exists, meaning the React app is already set up
if [ ! -f package.json ]; then
  echo "Creating new React app..."
  # Clean up any existing conflicting files like package-lock.json
  if [ -f package-lock.json ]; then
    echo "Removing existing package-lock.json to avoid conflicts..."
    rm package-lock.json
  fi

  # Create React app using npx (without create-react-app since it's deprecated)
  npx create-react-app@latest .
else
  echo "React app already exists, skipping creation."
fi

# Install client-side dependencies
npm install

# Install additional dependencies
npm install react-router-dom
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material

# Build the React app
npm run build
