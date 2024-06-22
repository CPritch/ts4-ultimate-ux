import os
import yaml
import shutil
import xml.etree.ElementTree as ET
import subprocess

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
            'mappings': []
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

def replace_file(src_file, dst_file):
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    shutil.copy2(src_file, dst_file)

def merge_xml(original_tree, new_tree):
    original_root = original_tree.getroot()
    new_root = new_tree.getroot()

    # Merge widgets
    original_widgets = original_root.find('widgets')
    new_widgets = new_root.find('widgets')
    if new_widgets is not None:
        if original_widgets is None:
            original_widgets = ET.SubElement(original_root, 'widgets')
        for new_widget in new_widgets:
            widget_name = new_widget.get('name')
            existing_widget = original_widgets.find(f".//widget[@name='{widget_name}']")
            if existing_widget is not None:
                original_widgets.remove(existing_widget)
            original_widgets.append(new_widget)

    # Merge gameStates
    original_game_states = original_root.find('gameStates')
    new_game_states = new_root.find('gameStates')
    if new_game_states is not None:
        if original_game_states is None:
            original_game_states = ET.SubElement(original_root, 'gameStates')
        for new_state in new_game_states:
            state_name = new_state.get('stateName')
            existing_state = original_game_states.find(f".//gameState[@stateName='{state_name}']")
            if existing_state is not None:
                for new_widget in new_state.findall('widget'):
                    widget_name = new_widget.get('name')
                    existing_widget = existing_state.find(f".//widget[@name='{widget_name}']")
                    if existing_widget is not None:
                        existing_state.remove(existing_widget)
                    existing_state.append(new_widget)
            else:
                original_game_states.append(new_state)

    return original_tree

def process_xml_files(config, base_dir) -> int:
    written_files = 0
    xml_config = config['source_files']['xml']
    src_dir = os.path.abspath(os.path.join(base_dir, xml_config['src']))
    export_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['export_dir']))
    output_dir = os.path.abspath(os.path.join(base_dir, config['build_options']['output_dir']))
    default_action = xml_config['action']
    mappings = xml_config['mappings']

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.xml'):
                src_file = os.path.join(root, file)
                relative_path = os.path.relpath(src_file, src_dir)
                
                # Check if there's a mapping for this file
                mapping = next((m for m in mappings if m.get('friendly_name') == file), {})
                
                export_filename = mapping.get('name', file)
                action = mapping.get('action', default_action)


                export_file = os.path.join(export_dir, os.path.dirname(relative_path), export_filename)
                output_file = os.path.join(output_dir, export_filename)

                if not os.path.exists(export_file):
                    print(f"Error: Could not find exported file: {export_filename}")
                    continue

                if action == 'replace':
                    replace_file(export_file, output_file)
                    print(f"Replaced {src_file} with {export_file}")
                    written_files += 1
                elif action == 'merge':
                    original_tree = ET.parse(src_file)
                    new_tree = ET.parse(export_file)
                    merged_tree = merge_xml(original_tree, new_tree)
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    merged_tree.write(output_file)
                    print(f"Merged {file} with {export_filename}")
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
            friendly_name = file_name.replace(".swf",".ScaleFormGFX")
            full_name = next((f for f in os.listdir(export_dir) if f.endswith(f'.{friendly_name}')), None)
            if full_name is None:
                print(f"Error: No matching file found for {file_name}")
                continue
        else:
            full_name = file_name

        export_file = os.path.join(export_dir, full_name)
        output_file = os.path.join(output_dir, full_name)

        print(src_dir)
        print(export_file)
        print(output_file)

        cmd = [
            "sims-swf-compiler",
            "-src", src_dir,
            "-dst", export_file,
            "-o", output_file
        ]

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