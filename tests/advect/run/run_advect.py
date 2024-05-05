"""Run model advect."""

import json
import multiprocessing as mp
from pathlib import Path
import sys
from timeit import default_timer


from rtmf6.run import main

def run_model(model_name):
    model_path = Path(__file__).parent / f'../models/{model_name}'
    phreeqcrm_yaml = model_path / f'{model_name}.yaml'
    main(model_path, phreeqcrm_yaml, reactions=True)

def run():
    start = default_timer()
    mp.set_start_method('spawn')
    specific_model_data = json.loads(Path(sys.argv[1]).read_text())
    run_model(model_name=specific_model_data['name'])
    print(default_timer() - start)

if __name__ == '__main__':
    run()
