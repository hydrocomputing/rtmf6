"""
Run all steps to create a model.

1. Create a new base model.
2. Clone the base model into component models.
3. Create PhreeqcRM yaml file.
"""

import json
from pathlib import Path
import sys

from make_base_model import make_input_data
from clone_model import make_all_component_models
from create_yaml import create_yaml


def do_steps(specific_model_data, base_path=None):
    """Do all preprocessing steps."""
    model_name = specific_model_data['name']
    geometry = specific_model_data['geometry']
    if base_path is None:
        base_path = Path(__file__).parent.parent
    models_path = base_path / 'models'
    model_path = models_path / model_name
    yaml_path = model_path / f'{model_name}.yaml'
    phreeqcrm_data_path = base_path / 'phreeqcrm_data'
    phreeqcrm_yaml = model_path / f'{model_name}.yaml'

    models_path.mkdir(exist_ok=True)
    model_path.mkdir(exist_ok=True)
    print('making base model')
    base_model_path = make_input_data(
        model_path, model_name, specific_model_data
    )

    nxyz = geometry['nlay'] * geometry['nrow'] * geometry['ncol']
    print(nxyz)
    create_yaml(
        file_name=yaml_path,
        data_path=phreeqcrm_data_path,
        nxyz=nxyz,
    )

    print('making component models')
    print(base_model_path)
    make_all_component_models(
        model_path=base_model_path,
        model_name=model_name,
        phreeqcrm_yaml=phreeqcrm_yaml,
        coords={'left': 0, 'right': geometry['ncol'] - 1},
    )


def main():
    """Run all steps."""
    specific_model_data = json.loads(Path(sys.argv[1]).read_text())
    do_steps(specific_model_data)


if __name__ == '__main__':
    main()
