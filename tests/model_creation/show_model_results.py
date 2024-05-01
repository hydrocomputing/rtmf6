"""Show test model."""

from pathlib import Path

import pandas as pd

from pymf6tools.make_model import run_simulation
from pymf6tools.plotting import show_bcs, show_heads, show_concentration


def show_results(model_name='advect'):
    """Create plots for model outputs."""
    model_path = Path(__file__).parent / f'../models/{model_name}'
    picture_path = model_path / 'pictures'
    picture_path.mkdir(exist_ok=True)

    def save_picture(plot, file_name, picture_path=picture_path):
        plot.figure.savefig(picture_path / file_name)

    run_simulation(model_path=model_path, verbosity_level=0)
    plot = show_bcs(model_path, model_name, bc_names=['chd'])
    save_picture(plot, 'bcs.png')
    plot = show_heads(
        model_path=model_path,
        name=model_name,
        title='',
        kstpkper=(800, 1),
        spdis_index=120,
        show_wells=False,
    )
    save_picture(plot, 'head.png')
    plot = show_concentration(
        model_path=model_path,
        name=model_name,
        kstpkper=(50, 1),
        show_wells=False,
        show_rivers=False,
        show_grid=False,
        vmin=20,
        vmax=40,
        layer=0,
    )
    save_picture(plot, 'conc.png')
    obs = pd.read_csv(model_path / 'gwt_advect.obs.csv')
    plot = obs.plot(x='time', y='CENTER_LAYER_0')
    plot.figure.savefig(picture_path / 'conc_breaktrough.png')


if __name__ == '__main__':
    show_results()
