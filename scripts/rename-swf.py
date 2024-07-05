import os
import re

def rename_files(directory):
    directory = os.path.join(directory, '')

    pattern = r'[0-9A-F]{8}![0-9A-F]{8}![0-9A-F]{16}\.(.+)\.ScaleFormGFX'

    for filename in os.listdir(directory):
        match = re.match(pattern, filename)
        if match:
            new_name = match.group(1) + '.swf'
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
            except OSError as e:
                print(f"Error renaming {filename}: {e}")
        else:
            print(f"Skipped: {filename} (doesn't match the expected format)")

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, '..'))
directory_path = './export/gfx' #DO NOT RENAME YOUR EXPORT IN /export/ui. Copy the swf files across to a new directory.
rename_files(os.path.abspath(os.path.join(base_dir, directory_path)))