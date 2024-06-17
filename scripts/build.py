import os
import yaml
import shutil

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
        },
        'scaleformgfx': {
            'src': './dst',
            'action': 'recompile',
            'actionscript':[]
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

with open(r'./build.yaml', 'r') as config_file:
    config = set_default_recursively(yaml.safe_load(config_file), default_options)

output_dir = os.path.abspath(config['build_options']['output_dir'])

if config['build_options']['clean_before_build'] == True:
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

print(f"Build complete and files written to {config['build_options']['output_dir']}")