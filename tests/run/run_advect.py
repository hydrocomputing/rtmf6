"""Run model advect."""

import multiprocessing as mp
from pathlib import Path

from rtmf6.run import main

def run(model_name):
    model_path = Path(__file__).parent / f'../models/{model_name}'
    phreeqcrm_yaml = Path(__file__).parent / '../phreeqpy/advect_cpp_exception.yaml'
    main(model_path, phreeqcrm_yaml, reactions=True)

if __name__ == '__main__':
    from timeit import default_timer
    start = default_timer()
    mp.set_start_method('spawn')
    run('advect')
    print(default_timer() - start)
