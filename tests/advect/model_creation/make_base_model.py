"""Create a simple test model."""

import json
from pathlib import Path
import sys

from pymf6_tools.make_model import make_input


def make_chd(
    initial_concentration, head_left, head_right, nrow, ncol, nlay, repeat_times
):
    """Create CHD BCs."""
    def make_one(sol_numbers=(1, 1)):
        chd = []
        for lay in range(nlay):
            for row in range(nrow):
                chd.append(
                    [(lay, row, 0), head_left,
                    float(initial_concentration * 2),
                    sol_numbers[0]  # solution number
                    ],
                    )
            for row in range(nrow):
                chd.append(
                    [(lay, row, ncol - 1), head_right,
                    float(initial_concentration),
                    sol_numbers[1]  # solution number
                    ],
                )
        return chd
    stress_period_data = {0: make_one(), 1: make_one((0, -1))}
    return stress_period_data


def make_obs(ncol, nrow, nlay):
    """Create observation wells."""
    data = []
    for lay in range(nlay):
        data.append((f'center_layer_{lay}', (lay, nrow // 2, ncol - 2)))
    return data


def make_model_data(model_path, geometry, time_steps, model_name=None, initial_concentration=0):
    """Create transport model data."""
    model_path = Path(model_path)
    nlay = geometry['nlay']
    nrow = geometry['nrow']
    ncol = geometry['ncol']
    repeat_times = 1
    head_left = 14
    head_right = 12
    model_data = {
        'model_path': model_path,
        'name': model_name if model_name else model_path.name,
        'transport': True,
        'reactive': True,
        'times': (
            2000.0,  # perlen (double) is the length of a stress period.
            time_steps,  # nstp (integer) is the number of time steps in a stress period.
            1.0,  # tsmult (double) is the multiplier for the length of successive
            # time steps.
        ),
        'time_units': 'DAYS',
        'length_units': 'meters',
        'repeat_times': repeat_times,  # nper = repeat_times + 1
        'nrow': nrow,
        'ncol': ncol,
        'nlay': nlay,
        'delr': geometry['delr'],
        'delc': geometry['delc'],
        'top': 15.0,
        'botm': [-5.0, -10.0, -15.0][:nlay],
        'k': [2, 0.000006, 0.5][:nlay],  # initial value of k
        'k33': [0.1, 0.002, 0.3][:nlay],  # vertical anisotropy
        'sy': 0.2,
        'ss': 0.000001,
        'initial_head': 14.0,
        'obs': make_obs(ncol=ncol, nrow=nrow, nlay=nlay),
        'chd': make_chd(
            ncol=ncol,
            nrow=nrow,
            nlay=nlay,
            head_left=head_left,
            head_right=head_right,
            repeat_times=repeat_times,
            initial_concentration=initial_concentration,
        ),
        'wells_active': False,
        'river_active': False,
        'initial_concentration': initial_concentration,
        'scheme': 'TVD', # 'UPSTREAM', # 'TVD',  # 'TVD' or 'UPSTREAM'
        'longitudinal_dispersivity': 0.0001,
        # Ratio of transverse to longitudinal dispersitivity
        'dispersivity_ratio': 0.01,
        'porosity': 0.2,
        'hclose_transport': 0.1,
        'nouter_transport': 500,
        'ninner_transport': 1000,
        'hclose_flow': 0.1,
        'nouter_flow': 500,
        'ninner_flow': 1000,
        'gwf_oc_head': 'LAST',
        'gwf_oc_budget': 'LAST',
        'gwt_oc_conc': 'LAST',
        'gwt_oc_budget': 'LAST',
    }
    return model_data


def make_input_data(model_path, model_name, specific_model_data):
    """Write model input files."""
    model_data = make_model_data(
        model_path=model_path,
        model_name=model_name,
        initial_concentration=0,
        geometry=specific_model_data['geometry'],
        time_steps=specific_model_data['time_steps']
    )
    make_input(model_data, verbosity_level=0)
    return model_path


def main(model_path=None):
    """Create the base model."""
    specific_model_data = json.loads(Path(sys.argv[1]).read_text())
    model_name = specific_model_data['name']
    print(model_name)
    print()
    # geometry = specific_model_data['geometry']
    # nthread = specific_model_data['nthread']
    if model_path is None:
        model_path = Path(sys.argv[2])
    print(model_path)
    print()
    make_input_data(model_path, model_name, specific_model_data)

if __name__ == '__main__':
    main()
