#!/usr/bin/env python3
"""
Direct patch script to fix the cached_download import issue in sentence-transformers
"""

import os
import sys
import subprocess

def find_sentence_transformers_path():
    """Find the sentence_transformers installation path"""
    try:
        result = subprocess.run([sys.executable, "-c", "import sentence_transformers; print(sentence_transformers.__file__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            st_path = os.path.dirname(result.stdout.strip())
            return st_path
    except:
        pass
    
    # Try to find it in common locations
    possible_paths = [
        os.path.join(os.path.expanduser("~"), ".local/lib/python3.*/site-packages/sentence_transformers"),
        "/usr/local/lib/python3.*/site-packages/sentence_transformers",
        "/usr/lib/python3.*/site-packages/sentence_transformers"
    ]
    
    for path_pattern in possible_paths:
        import glob
        matches = glob.glob(path_pattern)
        if matches:
            return matches[0]
    
    return None

def patch_sentence_transformers():
    """Patch the SentenceTransformer.py file to use hf_hub_download instead of cached_download"""
    
    # Find the sentence_transformers installation path
    st_path = find_sentence_transformers_path()
    
    if not st_path:
        print("Error: Could not find sentence_transformers installation path")
        return False
    
    sentence_transformer_file = os.path.join(st_path, 'SentenceTransformer.py')
    
    if not os.path.exists(sentence_transformer_file):
        print(f"Error: Could not find SentenceTransformer.py at {sentence_transformer_file}")
        return False
    
    print(f"Patching file: {sentence_transformer_file}")
    
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
        # Let's check if it's already patched
        if new_import in content:
            print("Import statement appears to be already patched")
        else:
            print("Available imports in the file:")
            for line in content.split('\n'):
                if 'from huggingface_hub import' in line:
                    print(f"  {line.strip()}")
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