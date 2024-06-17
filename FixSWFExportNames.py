import os

# Define the directory path where the files are located
# Warning will destructively rename all the files to their importable name in JPEXS
directory_path = './export/ui/'

# Loop through each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.ScaleFormGFX'):
        base_new_name = filename.split('.')[1]
        new_name = base_new_name + '.swf'
        counter = 0
        while os.path.exists(os.path.join(directory_path, new_name)):
            new_name = f"{base_new_name}_{counter}.swf"
            counter += 1
        os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_name))

print("Files have been renamed.")
