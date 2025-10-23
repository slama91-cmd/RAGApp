#!/bin/bash

echo "Fixing dependency compatibility issues..."

# Uninstall problematic packages
echo "Uninstalling sentence-transformers, timm, and huggingface-hub..."
pip uninstall -y sentence-transformers timm huggingface-hub

# Reinstall with compatible versions
echo "Installing compatible versions..."
pip install huggingface-hub==0.35.3
pip install sentence-transformers==2.2.2
pip install timm==0.9.5

echo "Dependencies fixed successfully!"
echo "Please restart the API server with: python api.py"