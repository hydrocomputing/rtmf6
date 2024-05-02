"""Run model advect."""

import multiprocessing as mp
from pathlib import Path

from rtmf6.run import main

def run(model_name):
    model_path = Path(__file__).parent / f'../models/{model_name}'
    main(model_path)

if __name__ == '__main__':
    mp.set_start_method('spawn')
    run('advect')
