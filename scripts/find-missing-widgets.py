import os
import xml.etree.ElementTree as ET
import subprocess
import sys
from collections import defaultdict
import time
import random

def get_widget_names(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return [widget.attrib['name'] for widget in root.findall('.//widgets/widget')]

def run_with_retry(cmd, max_retries=5, initial_delay=1, max_delay=60):
    retries = 0
    while retries < max_retries:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, PermissionError) as e:
            print(f"Error on attempt {retries + 1}: {str(e)}")
            retries += 1
            if retries >= max_retries:
                raise
            delay = min(initial_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
            print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

def search_swfs(directory, widget_names):
    found_widgets = defaultdict(list)
    for file in os.listdir(directory):
        if file.endswith('.swf'):
            swf_path = os.path.join(directory, file)
            print(f"Analyzing {swf_path}...")
            try:
                commands = ['-dumpSWF', '-dumpAS2', '-dumpAS3']
                
                for command in commands:
                    ffdec_path = r"C://Program Files (x86)//FFDec//ffdec.jar"
                    c = ['java', '-jar', ffdec_path, '-cli', command, swf_path]
                    print(" ".join(c))
                    result = run_with_retry(c)
                    
                    for widget_name in widget_names:
                        if widget_name in result.stdout:
                            found_widgets[widget_name].append((file, command))
                
                print("Analysis complete!")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {swf_path}")
                print(f"Exit code: {e.returncode}")
                print(f"Standard output: {e.stdout}")
                print(f"Error output: {e.stderr}")
                sys.exit(1)  # Stop the script after the first error
            except FileNotFoundError:
                print("Error: FFDEC not found. Make sure it's installed and in your system PATH.")
                sys.exit(1)
    
    return found_widgets

def write_results(widget_names, found_widgets, output_file):
    with open(output_file, 'w') as f:
        f.write("Results:\n")
        for widget in widget_names:
            if widget in found_widgets:
                f.write(f"Found '{widget}' in:\n")
                for file, command in found_widgets[widget]:
                    f.write(f"  - {file} ({command})\n")
            else:
                f.write(f"'{widget}' not found in any SWF\n")
        f.write("\n")

def main():
    xml_file = './export/ui/0333406C!00000000!DE3FB8F4E5C1A9E5.FontConfiguration.xml'
    swf_directory = './export/gfx'
    output_file = 'widget_search_results.txt'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..'))

    widget_names = get_widget_names(os.path.join(base_dir, xml_file))
    swf_directory_full = os.path.join(base_dir, swf_directory)

    found_widgets = search_swfs(swf_directory_full, widget_names)
    
    write_results(widget_names, found_widgets, output_file)
    print(f"Results have been written to {output_file}")

if __name__ == "__main__":
    main()