"""Plot simulation results"""

from pathlib import Path

import pandas as pd


species_colors = {
    'Na': 'C0',  # blue
    'Cl': 'C1',  # orange
    'K': 'C2',  # green
    'Ca': 'C3',  # red
}


def read_conc_rtmf6(
    model_name,
    component_models_dir,
    components=('Na', 'Cl', 'K', 'Ca'),
    steps=None,
):
    """Plot concentrations."""
    conc = {}
    for path in component_models_dir.glob('*'):
        name = path.name
        if name in components:
            value = pd.read_csv(
                path / f'gwt_{model_name}.obs.csv',
                nrows=steps,
            )[['time', 'CONCENTRATION']]
            value.columns = ['time', name]
            value[name] *= 1_000
            conc[name] = value
    res = conc[components[0]]
    for name in components[1:]:
        res = pd.merge(res, conc[name])
    return res.set_index('time')


def read_conc_pht3d(file_name):
    df = pd.read_csv(file_name, sep=r'\s+', index_col='time_d')
    df.index.name = 'time'
    clean_df = df[df.cell == 40].drop(columns=['cell']) * 1_000
    return clean_df


def join_conc_rtmf6_pht3d(rtmf6_df, pht3d_df):
    rtmf6_sel = rtmf6_df.loc[pht3d_df.index]
    rtmf6 = rtmf6_sel.copy()
    pht3d = pht3d_df.copy()
    rtmf6.columns = [col + ' rtmf6' for col in rtmf6.columns]
    pht3d.columns = [col + ' pht3d' for col in pht3d.columns]
    return rtmf6.join(pht3d)


def plot_joined(joined):
    species_colors = {
        species: f'C{n}'
        for n, species in enumerate(
            dict.fromkeys(col.split()[0] for col in joined.columns)
        )
    }
    line_styles = {'rtmf6': '-', 'pht3d': '--'}
    styles = []
    for col in joined.columns:
        species, model_type = col.split()
        styles.append(f'{species_colors[species]}{line_styles[model_type]}')
    return joined.plot(
        xlabel='time (days)',
        ylabel=' concentrations (mmols/kgw)',
        style=styles,
    )


def plot_advect(
    model_name,
    component_models_dir,
    components=('Na', 'Cl', 'K', 'Ca'),
    steps=None,
):
    """Plot concentrations."""
    df = read_conc_rtmf6(
        model_name=model_name,
        component_models_dir=component_models_dir,
        components=components,
        steps=steps,
    )
    return df.plot(x='time', ylabel='mmols/kgw')


def plot_compare_rtmf6_pht3d(
    config,
    pht3d_file,
    components=('Na', 'Cl', 'K', 'Ca'),
    steps=None,
    save_fig=None,
):
    """Plot concentrations."""
    model_name = config.project_settings['project']['name']
    component_models_dir = config.internal_paths.component_models_path
    rtmf6_df = read_conc_rtmf6(
        model_name=model_name,
        component_models_dir=component_models_dir,
        components=components,
        steps=steps,
    )
    pht3d_df = read_conc_pht3d(pht3d_file)
    joined = join_conc_rtmf6_pht3d(rtmf6_df, pht3d_df)
    fig = plot_joined(joined)
    if save_fig:
        fig.figure.savefig(save_fig)
    return fig
