import os
import yaml
import shutil
import xml.etree.ElementTree as ET
import subprocess
import platform

default_options = {
    'build_options': {
        'clean_before_build': True,
        'export_dir': './export/ui',
        'output_dir': './build/ui',
        'package_file': './build/UltimateUX.package'
    },
    'source_files': {
        'xml': {
            'action': 'merge',
            'src': './src',
            'mappings': [],
            'merge_keys': []
        },
        'scaleformgfx': {
            'src': './dst',
            'action': 'recompile',
            'imports':[],
            'mappings': []
        }
    }
}

def set_default_recursively(tgt, default):
    for k in default:
        if isinstance(default[k], dict):
            if not tgt.get(k):
                tgt[k] = default[k]
            tgt[k] = set_default_recursively(tgt[k], default[k])
        else:
            tgt.setdefault(k, default[k])
    return tgt

def merge_xml_nodes(org_node, new_node, merge_keys):
    for new_child in new_node:
        attributes = [key for key in merge_keys if new_child.get(key)]
        if len(attributes) > 0:
            merge_child = org_node.find(f".//{new_child.tag}[@{attributes[0]}='{new_child.get(attributes[0])}']")
            if merge_child is not None:
                merge_xml_nodes(merge_child, new_child, merge_keys)
            else:
                org_node.append(new_child)
        else:
            org_children = org_node.findall(f".//{new_child.tag}")
            if len(org_children) == 1:
                merge_xml_nodes(org_children[0], new_child, merge_keys)
            else:
                org_node.append(new_child)

def merge_xml_files(org_file, new_file, merge_keys):
    org_name = org_file.split("\\")[-1]
    new_name = new_file.split("\\")[-1]
    print(f"Merging {org_name} with {new_name} using {merge_keys}")
    org_root = ET.parse(org_file).getroot()
    new_root = ET.parse(new_file).getroot()
    if org_root.tag != new_root.tag:
        raise Exception("Root XML tags do not match")
    merge_xml_nodes(org_root, new_root, merge_keys)
    return ET.tostring(org_root, encoding="unicode")


def process_xml_files(config, base_dir) -> int:
    written_files = 0
    xml_config = config['source_files']['xml']
    src_dir = os.path.abspath(os.path.join(base_dir, xml_config['src']))
    export_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['export_dir']))
    output_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['output_dir']))
    default_action = xml_config['action']
    mappings = xml_config['mappings']
    merge_keys = xml_config['merge_keys']

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.xml'):
                src_file = os.path.join(root, file)
                relative_path = os.path.relpath(src_file, src_dir)
                
                mapping = next((m for m in mappings if m.get('friendly_name') == file), {})
                
                export_filename = mapping.get('name', file)
                action = mapping.get('action', default_action)

                export_file = os.path.join(export_dir, os.path.dirname(relative_path), export_filename)
                output_file = os.path.join(output_dir, export_filename)

                if not os.path.exists(export_file):
                    print(f"Error: Could not find exported file: {export_filename}")
                    continue

                if action == 'replace':
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    shutil.copy2(export_file, output_file)
                    print(f"Replaced {file}")
                    written_files += 1
                elif action == 'merge':
                    merged_xml = merge_xml_files(export_file, src_file, merge_keys + mapping.get('merge_keys',[]))
                    with open(output_file, 'w') as out:
                        out.write(merged_xml)
                    print(f"Merged {file}")
                    written_files += 1
                else:
                    print(f"Error: Unknown action '{action}' for {src_file}")
    return written_files

def process_scaleformgfx_files(config, base_dir) -> int:
    written_files = 0
    scaleformgfx_config = config['source_files']['scaleformgfx']
    export_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['export_dir']))
    output_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['output_dir']))

    for import_file in scaleformgfx_config.get('imports', []):
        file_name = import_file['file']
        src_dir = os.path.abspath(os.path.join(base_dir, import_file['src']))

        if file_name.endswith('.swf'):
            friendly_name = file_name.replace(".swf", ".ScaleFormGFX")
            full_name = next((f for f in os.listdir(export_dir) if f.endswith(f'.{friendly_name}')), None)
            if full_name is None:
                print(f"Error: No matching file found for {file_name}")
                continue
        else:
            full_name = file_name

        export_file = os.path.join(export_dir, full_name)
        output_file = os.path.join(output_dir, full_name)

        if platform.system() == 'Windows':
            cmd = ["sims-swf-compiler.bat"]
        else:
            cmd = ["sh", "sims-swf-compiler.sh"]

        cmd.extend(["-src", src_dir, "-dst", export_file, "-out", output_file])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if "Modified SWF saved" in result.stdout:
                print(f"Successfully processed {file_name}")
                written_files += 1
            else:
                print(f"Warning: 'Modified SWF saved' not found in output for {file_name}")
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {file_name}: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")

    return written_files

def main():
    written_files = 0
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..'))
    os.chdir(script_dir)

    with open(os.path.join(base_dir, 'build.yaml'), 'r') as config_file:
        config = set_default_recursively(yaml.safe_load(config_file), default_options)

    output_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['output_dir']))

    if config['build_options']['clean_before_build']:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    for file_type in config['source_files']:
        if file_type == 'xml':
            written_files += process_xml_files(config, base_dir)
        elif file_type == 'scaleformgfx':
            written_files += process_scaleformgfx_files(config, base_dir)
        else:
            print(f"Error: Unimplemented file type '{file_type}'")

    print(f"Build complete: {written_files} files written to {config['build_options']['output_dir']}")

if __name__ == "__main__":
    main()