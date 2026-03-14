from pathlib import Path
import shelve
from pymf6.mf6 import MF6


def get_const(model_path, model_name, const_name, time_step, dir_name='equilibrium_phases'):
    mf6 = MF6(sim_path=model_path / 'mf6')
    transport_models = mf6.models['gwt6']
    gwt = transport_models[model_name]
    with shelve.open(model_path / 'out' / dir_name /f'{const_name}.shelve') as sobj:
        res = sobj[str(time_step)].reshape(gwt.shape)
    return res

if __name__ == '__main__':
    model_path = Path('..')
    model_name = 'gwt_ex10_simple'
    phase_name = 'Calcite'
    time_step = 1
    print(get_const(model_path, model_name, phase_name, time_step))
    phase_name = 'Al'
    print(get_const(model_path, model_name, phase_name, time_step, dir_name='concentrations'))