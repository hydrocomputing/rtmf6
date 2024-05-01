"""
Clone a MODFLOW model.

This reads all model input files with flopy, modifies some values such
as initial concentrations and concnetration values of boundary,
and writes files back.
"""

from pathlib import Path

from rtmf6.preprocessing.simulation import Simulation


COORDS = {'left': 0, 'right': 9}

conc_values = {
    'Ca': 0.6,
    'Cl': 1.2,
    'Na': 1.0,
    'K': 0.2,
    'N': 1.2,
    'O': 55.34157223695579,
    'H': 110.68207753009322,
    'Charge': 0.0,
}

CONCENTRATIONS = {
    'Ca': {
        'init_conc': 0.0,
        'new_chd_data': {
            0: {'left': 0.0, 'right': 0.0},
            1: {'left': conc_values['Ca'], 'right': 0.0},
        },
    },
    'Cl': {
        'init_conc': 0,
        'new_chd_data': {
            0: {'left': 0.0, 'right': 0.0},
            1: {'left': conc_values['Cl'], 'right': 0.0},
        },
    },
    'Na': {
        'init_conc': conc_values['Na'],
        'new_chd_data': {
            0: {'left': conc_values['Na'], 'right': conc_values['Na']},
            1: {'left': 0.0, 'right': 0.0},
        },
    },
    'K': {
        'init_conc': conc_values['K'],
        'new_chd_data': {
            0: {'left': conc_values['K'], 'right': conc_values['K']},
            1: {'left': 0.0, 'right': 0.0},
        },
    },
    'N': {
        'init_conc': conc_values['N'],
        'new_chd_data': {
            0: {'left': conc_values['N'], 'right': conc_values['N']},
            1: {'left': 0.0, 'right': 0.0},
        },
    },
    'O': {
        'init_conc': conc_values['O'],
        'new_chd_data': {
            0: {'left': conc_values['O'], 'right': conc_values['O']},
            1: {'left': conc_values['O'], 'right': conc_values['O']},
        },
    },
    'H': {
        'init_conc': conc_values['H'],
        'new_chd_data': {
            0: {'left': conc_values['H'], 'right': conc_values['H']},
            1: {'left': conc_values['H'], 'right': conc_values['H']},
        },
    },
    'Charge': {
        'init_conc': conc_values['Charge'],
        'new_chd_data': {
            0: {'left': conc_values['Charge'], 'right': conc_values['Charge']},
            1: {'left': conc_values['Charge'], 'right': conc_values['Charge']},
        },
    },
}


def modfify_chd_data(chd_data, new_chd_data, coords=COORDS):
    """Set new concentration values for CHD."""
    for stress_period_number, values in new_chd_data.items():
        chd_data_period = chd_data[stress_period_number]
        for side, value in values.items():
            row_index = coords[side]
            for bc in chd_data_period:
                if bc[0][-1] == row_index:
                    bc[-1] = value
    return chd_data


def make_sub_model(model_path, name, data, chd_name='chd-1'):
    """Create sub model."""
    sim = Simulation(model_path)
    cloned = sim.clone(sub=name)
    cloned.set_const_init_conc(data['init_conc'])
    chd_data = sim.get_stress_period_data(
        model_type='flow', package_name=chd_name
    )
    modfify_chd_data(chd_data, data['new_chd_data'])
    cloned.set_stress_period_data(
        model_type='flow', package_name=chd_name, data=chd_data
    )
    cloned.write_back()


def main(model_name='advect', concentrations=CONCENTRATIONS):
    """Write model input files for all submodels."""
    model_path = Path(__file__).parent / f'../models/{model_name}'
    for name, data in concentrations.items():
        make_sub_model(model_path=model_path, name=name, data=data)


if __name__ == '__main__':
    main()
