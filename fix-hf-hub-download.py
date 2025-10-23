#!/usr/bin/env python3
"""
Fix script to properly replace cached_download with hf_hub_download in sentence-transformers
"""

import os
import subprocess

def fix_util_py():
    """Fix the util.py file to properly use hf_hub_download instead of cached_download"""
    
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
    
    # Replace the problematic section
    old_code = """        hf_hub_download_args = {'url': url,
            'cache_dir': storage_folder,
            'force_filename': relative_filepath,
            'library_name': library_name,
            'library_version': library_version,
            'user_agent': user_agent,
            'use_auth_token': use_auth_token}

        if version.parse(huggingface_hub.__version__) >= version.parse("0.8.1"):
            # huggingface_hub v0.8.1 introduces a new cache layout. We sill use a manual layout
            # And need to pass legacy_cache_layout=True to avoid that a warning will be printed
            hf_hub_download_args['legacy_cache_layout'] = True

        path = hf_hub_download(**hf_hub_download_args)"""
    
    new_code = """        # Use http_get to download the file directly since hf_hub_download has different parameters
        from huggingface_hub.utils import http_get
        from huggingface_hub.file_download import _get_cache_file_to_download
        
        # Create the target path
        target_path = os.path.join(storage_folder, relative_filepath)
        
        # Download the file
        http_get(url, target_path, library_name=library_name, library_version=library_version, 
                user_agent=user_agent, use_auth_token=use_auth_token)
        
        path = target_path"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("Successfully patched the download function")
    else:
        print("Warning: Could not find the exact code section to patch")
        return False
    
    # Write the patched content back
    with open(util_file, 'w') as f:
        f.write(content)
    
    print("Patch completed successfully!")
    return True

if __name__ == "__main__":
    fix_util_py()