"""
Run all steps to create a model.

1. Create a new base model.
2. Clone the base model into component models.
3. Create PhreeqcRM yaml file.
"""

from pathlib import Path
from make_base_model import make_input_data
from clone_model import make_all_component_models
from create_yaml import create_yaml


# GEOMETRY = dict(nlay=3, nrow=10, ncol=10, delr=10.0, delc=10.0)
# MODEL_NAME = 'advect1'
# MODEL_NAME = 'advect1n'
#GEOMETRY = dict(nlay=1, nrow=3, ncol=100, delr=1.0, delc=1.0)
# MODEL_NAME = 'advect2'
# MODEL_NAME = 'advect2n'
# GEOMETRY = dict(nlay=1, nrow=3, ncol=200, delr=0.5, delc=0.5)
# MODEL_NAME = 'advect3'
# GEOMETRY = dict(nlay=1, nrow=3, ncol=10, delr=10.0, delc=10.0)
# MODEL_NAME = 'advect4'
# GEOMETRY = dict(nlay=1, nrow=3, ncol=1000, delr=0.1, delc=0.1)
# MODEL_NAME = 'advect5'
# GEOMETRY = dict(nlay=1, nrow=1, ncol=10, delr=10.0, delc=10.0)
# MODEL_NAME = 'advect6'
# MODEL_NAME = 'advect6n'

MODEL_NAME = 'advect7'
GEOMETRY = dict(nlay=1, nrow=1, ncol=100, delr=1.0, delc=1.0)

BASE_PATH = Path(__file__).parent.parent
MODEL_PATH = BASE_PATH / 'models' / MODEL_NAME
YAML_PATH = MODEL_PATH / f'{MODEL_NAME}.yaml'
PHREEQCRM_DATA_PATH = BASE_PATH / 'phreeqcrm_data'


def do_steps(model_path=MODEL_PATH, model_name=MODEL_NAME, geometry=GEOMETRY):
    model_path.mkdir(exist_ok=True)
    base_model_path = make_input_data(model_path, model_name=model_name, geometry=geometry)
    make_all_component_models(
        model_path=base_model_path,
        model_name=model_name,
        coords={'left': 0, 'right': geometry['ncol'] - 1}
        )
    nxyz = geometry['nlay'] * geometry['nrow'] * geometry['ncol']
    print(nxyz)
    create_yaml(
        file_name=YAML_PATH,
        data_path=PHREEQCRM_DATA_PATH,
        nxyz=nxyz,
        )


if __name__ == '__main__':
    do_steps()