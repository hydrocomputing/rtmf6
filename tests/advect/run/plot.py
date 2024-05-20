from pathlib import Path

import pandas as pd

def plot(model_name, components=('Na', 'Cl', 'K', 'Ca')):
    """Plot concentrations."""
    component_models_dir = Path(__file__).parent / f'../models/{model_name}' / 'component_models'
    conc = {}
    for path in component_models_dir.glob('*'):
        name = path.name
        if name in components:
            value = pd.read_csv(path / f'gwt_{model_name}.obs.csv')[['time', 'CENTER_LAYER_0']]
            value.columns = ['time', name]
            value[name] *= 1_000
            conc[name] = value
    res = conc[components[0]]
    for name in components[1:]:
        res = pd.merge(res, conc[name])
    res.plot(x='time')


if __name__ == '__main__':
    plot('advect1')