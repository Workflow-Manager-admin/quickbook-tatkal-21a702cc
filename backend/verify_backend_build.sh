#!/bin/bash

set -e

# This script attempts to build, migrate, and check the Django backend for common build/startup errors.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  chmod +x "$0"
fi

echo "=== [1/3] Installing dependencies from requirements.txt ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [2/3] Running Django makemigrations & migrate ==="
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput

echo "=== [3/3] Checking for critical Django import/startup errors ==="
python manage.py check

echo "=== Backend build verification succeeded! ==="
