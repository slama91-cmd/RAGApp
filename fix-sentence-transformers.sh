#!/bin/bash
echo "Fixing sentence-transformers compatibility with huggingface-hub..."

# First, uninstall all problematic packages
echo "Uninstalling sentence-transformers and huggingface-hub..."
pip uninstall -y sentence-transformers huggingface-hub

# Install a compatible version of huggingface-hub first
echo "Installing compatible huggingface-hub version..."
pip install huggingface-hub==0.10.1

# Now install sentence-transformers
echo "Installing sentence-transformers..."
pip install sentence-transformers==2.2.2

echo "Fix completed!"