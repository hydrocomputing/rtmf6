"""Reactive transport modeling with MODFLOW 6."""

import warnings
import sys

import multiprocessing as mp

from rtmf6.config import Config
from rtmf6.run import run_rtmf6
from rtmf6.preprocessing.create_inputs import make_inputs


def main(project_toml):
    """Run rtmf6 model."""
    # options to be read from CLI args
    # default values:
    reactions = True
    develop = False
    preprocess_only = False
    run_only = False

    if preprocess_only and run_only:
        raise ValueError('preprocess_only and run_only cannot both be True')

    if develop:
        print('Development mode active, showing deprecation warnings.')
        warnings.filterwarnings('ignore', category=DeprecationWarning)

    print('rtmf6 - A reactive transport model based on MODFLOW 6 and PhreeqcRM.')
    if not develop:
        warnings.filterwarnings('ignore', category=DeprecationWarning)
    config = Config(project_toml)

    if not run_only:
        print('Creating input files...')
        make_inputs(config)
        if preprocess_only:
            print('Preprocessing only, exiting.')
            sys.exit(0)

    print('Running rtmf6...')
    run_rtmf6(config, reactions=reactions)
    print()
    print('rtmf6 run complete.')


if __name__ == '__main__':
    mp.set_start_method('spawn')
    main(sys.argv[1])
