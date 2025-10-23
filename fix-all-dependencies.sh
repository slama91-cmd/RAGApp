#!/bin/bash

echo "Fixing all dependency compatibility issues..."

# Uninstall all problematic packages
echo "Uninstalling sentence-transformers, timm, huggingface-hub, transformers, and torch..."
pip uninstall -y sentence-transformers timm huggingface-hub transformers torch torchvision

# Reinstall with compatible versions
echo "Installing compatible versions..."
pip install torch==2.0.1 torchvision==0.15.2
pip install transformers==4.30.0
pip install huggingface-hub==0.14.1
pip install sentence-transformers==2.2.2
pip install timm==0.9.5

echo "All dependencies fixed successfully!"
echo "Please restart the API server with: python api.py"