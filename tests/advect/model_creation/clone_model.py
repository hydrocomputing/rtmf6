"""
Clone a MODFLOW model.

This reads all model input files with flopy, modifies some values such
as initial concentrations and concnetration values of boundary,
and writes files back.
"""

from phreeqpy.phreeqcrm.rm_model import PhreeqcRMModel

from rtmf6.preprocessing.simulation import Simulation


def make_concentrations(phreeqcrm_yaml):
    """Create concentrations values."""
    phreeqcrm_model = PhreeqcRMModel(str(phreeqcrm_yaml))
    bc_conc = phreeqcrm_model.get_initial_concentrations(0)
    init_conc = phreeqcrm_model.get_initial_concentrations(1)

    concentrations = {
        'Ca': {
            'init_conc': 0.0,
            'new_chd_data': {
                0: {'left': 0.0, 'right': 0.0},
                1: {'left': bc_conc['Ca'], 'right': 0.0},
            },
        },
        'Cl': {
            'init_conc': 0,
            'new_chd_data': {
                0: {'left': 0.0, 'right': 0.0},
                1: {'left': bc_conc['Cl'], 'right': 0.0},
            },
        },
        'Na': {
            'init_conc': init_conc['Na'],
            'new_chd_data': {
                0: {'left': init_conc['Na'], 'right': init_conc['Na']},
                1: {'left': 0.0, 'right': 0.0},
            },
        },
        'K': {
            'init_conc': init_conc['K'],
            'new_chd_data': {
                0: {'left': init_conc['K'], 'right': init_conc['K']},
                1: {'left': 0.0, 'right': 0.0},
            },
        },
        'N': {
            'init_conc': init_conc['N'],
            'new_chd_data': {
                0: {'left': init_conc['N'], 'right': init_conc['N']},
                1: {'left': 0.0, 'right': 0.0},
            },
        },
        'O': {
            'init_conc': init_conc['O'],
            'new_chd_data': {
                0: {'left': init_conc['O'], 'right': init_conc['O']},
                1: {'left': init_conc['O'], 'right': init_conc['O']},
            },
        },
        'H': {
            'init_conc': init_conc['H'],
            'new_chd_data': {
                0: {'left': init_conc['H'], 'right': init_conc['H']},
                1: {'left': init_conc['H'], 'right': init_conc['H']},
            },
        },
        'Charge': {
            'init_conc': init_conc['Charge'],
            'new_chd_data': {
                0: {'left': init_conc['Charge'], 'right': init_conc['Charge']},
                1: {'left': init_conc['Charge'], 'right': init_conc['Charge']},
            },
        },
    }
    return concentrations


def modfify_chd_data(chd_data, new_chd_data, coords):
    """Set new concentration values for CHD."""
    for stress_period_number, values in new_chd_data.items():
        chd_data_period = chd_data[stress_period_number]
        for side, value in values.items():
            row_index = coords[side]
            for bc in chd_data_period:
                if bc[0][-1] == row_index:
                    bc[-1] = value
    return chd_data


def make_component_model(sim, component, data, coords, chd_name='chd-1'):
    """Create one component model."""
    cloned = sim.clone(component=component)
    cloned.set_const_init_conc(data['init_conc'])
    chd_data = sim.get_stress_period_data(
        model_type='flow', package_name=chd_name
    )
    modfify_chd_data(chd_data, data['new_chd_data'], coords=coords)
    cloned.set_stress_period_data(
        model_type='flow', package_name=chd_name, data=chd_data
    )
    cloned.write_back()


def make_all_component_models(model_path, model_name, phreeqcrm_yaml, coords):
    """Write model input files for all component models."""
    concentrations = make_concentrations(phreeqcrm_yaml)
    sim = Simulation(model_path, model_name)
    for component, data in concentrations.items():
        make_component_model(sim,  component=component,
                              data=data, coords=coords)
