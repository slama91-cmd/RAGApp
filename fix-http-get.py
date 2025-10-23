#!/usr/bin/env python3
"""
Fix script to properly replace http_get import in sentence-transformers
"""

import os
import subprocess

def fix_util_py():
    """Fix the util.py file to properly use the correct http_get import"""
    
    # Find the sentence_transformers installation path
    result = subprocess.run(['find', os.path.expanduser('~/.local/lib'), '-name', 'util.py', '-path', '*/sentence_transformers/*'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error: Could not find util.py in sentence_transformers")
        return False
    
    util_file = result.stdout.strip()
    print(f"Patching file: {util_file}")
    
    # Read the file
    with open(util_file, 'r') as f:
        content = f.read()
    
    # Replace the problematic import
    old_import = "from huggingface_hub.utils import http_get"
    new_import = "from huggingface_hub.utils import get_from_cache"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("Successfully patched the import statement")
    else:
        print("Warning: Could not find the import statement to patch")
        return False
    
    # Replace the function call
    old_function_call = """        # Use http_get to download the file directly since hf_hub_download has different parameters
        from huggingface_hub.utils import http_get
        from huggingface_hub.file_download import _get_cache_file_to_download
        
        # Create the target path
        target_path = os.path.join(storage_folder, relative_filepath)
        
        # Download the file
        http_get(url, target_path, library_name=library_name, library_version=library_version, 
                user_agent=user_agent, use_auth_token=use_auth_token)
        
        path = target_path"""
    
    new_function_call = """        # Use requests to download the file directly since hf_hub_download has different parameters
        import requests
        
        # Create the target path
        target_path = os.path.join(storage_folder, relative_filepath)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Download the file
        headers = {'user-agent': user_agent}
        if use_auth_token:
            headers['authorization'] = f'Bearer {use_auth_token}'
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        path = target_path"""
    
    if old_function_call in content:
        content = content.replace(old_function_call, new_function_call)
        print("Successfully patched the download function")
    else:
        print("Warning: Could not find the exact function call to patch")
        return False
    
    # Write the patched content back
    with open(util_file, 'w') as f:
        f.write(content)
    
    print("Patch completed successfully!")
    return True

if __name__ == "__main__":
    fix_util_py()