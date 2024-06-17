import os
import yaml
import shutil
import xml.etree.ElementTree as ET

default_options = {
    'build_options': {
        'clean_before_build': True,
        'export_dir': './export/ui',
        'output_dir': './build/ui'
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
            'actionscript':[],
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

def main():
    written_files = 0
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..'))  # Get the parent directory of the script
    os.chdir(script_dir)  # Change working directory to the script's directory

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
        else:
            print(f"Error: Unimplemented file type '{file_type}'")

    print(f"Build complete: {written_files} files written to {config['build_options']['output_dir']}")

if __name__ == "__main__":
    main()