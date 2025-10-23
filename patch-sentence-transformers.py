#!/usr/bin/env python3
"""
Patch script to fix the cached_download import issue in sentence-transformers
"""

import os
import sys

def patch_sentence_transformers():
    """Patch the SentenceTransformer.py file to use hf_hub_download instead of cached_download"""
    
    # Find the sentence_transformers installation path
    import sentence_transformers
    st_path = os.path.dirname(sentence_transformers.__file__)
    sentence_transformer_file = os.path.join(st_path, 'SentenceTransformer.py')
    
    if not os.path.exists(sentence_transformer_file):
        print(f"Error: Could not find SentenceTransformer.py at {sentence_transformer_file}")
        return False
    
    # Read the file
    with open(sentence_transformer_file, 'r') as f:
        content = f.read()
    
    # Replace the import statement
    old_import = "from huggingface_hub import HfApi, HfFolder, Repository, hf_hub_url, cached_download"
    new_import = "from huggingface_hub import HfApi, HfFolder, Repository, hf_hub_url, hf_hub_download"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print(f"Successfully patched import in {sentence_transformer_file}")
    else:
        print(f"Warning: Could not find the import statement to patch in {sentence_transformer_file}")
        return False
    
    # Replace all occurrences of cached_download with hf_hub_download
    old_function = "cached_download"
    new_function = "hf_hub_download"
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print(f"Successfully patched function calls in {sentence_transformer_file}")
    else:
        print(f"Warning: Could not find any cached_download function calls to patch")
        return False
    
    # Write the patched content back
    with open(sentence_transformer_file, 'w') as f:
        f.write(content)
    
    print("Patch completed successfully!")
    return True

if __name__ == "__main__":
    patch_sentence_transformers()