"""Configuration."""

import sys
from pathlib import Path

import tomllib


class Config:
    """Configure a project."""
     # pylint: disable=too-many-instance-attributes, too-few-public-methods
    def __init__(self, project_toml):
        with open(project_toml, 'rb') as fobj:
            self.project_settings = tomllib.load(fobj)
        self._check()
        self.project_name = self.project_settings['project']['name']
        directory = self.project_settings['project'].get('directory', '.')
        self.project_path = Path(project_toml).parent.absolute() / directory
        self.reaction_model_name = self.project_settings['models'][
            'reaction_models'
        ][0]
        self.phreeqcrm_cell_value_categories = {
            'initial_concentrations': 'YAMLInitialSolutions2Module',
            'exchanges': 'YAMLInitialExchanges2Module',
            'equilibrium_phases': 'YAMLInitialEquilibriumPhases2Module',
            'gas_phases': 'YAMLInitialGasPhases2Module',
            'kinetics': 'YAMLInitialKinetics2Module',
            'solid_solutions': 'YAMLInitialSolidSolutions2Module',
            'surfaces': 'YAMLInitialSurfaces2Module',
        }
        self._set_path()
        self._make_path_absolute()
        self.reaction_start_stress_range = self._get_stress_period_range()

    def _get_stress_period_range(self):
        models = self.project_settings['models']
        reaction_start_stress_period = int(
            models.get('reaction_start_stress_period', 0)
        )
        reaction_end_stress_period = int(
            models.get('reaction_end_stress_period', sys.maxsize)
        )
        if reaction_start_stress_period > reaction_end_stress_period:
            raise ValueError(
                'reaction_end_stress_period must be equal or larger than '
                'reaction_start_stress_period\n'
                f'found {reaction_start_stress_period=} and {reaction_end_stress_period=}'
            )
        msg = 'stress period must have positive value found'
        if reaction_start_stress_period < 0:
            raise ValueError(f'{msg} {reaction_start_stress_period=}')
        if reaction_end_stress_period < 0:
            raise ValueError(f'{msg} {reaction_end_stress_period=}')
        return (reaction_start_stress_period, reaction_end_stress_period)

    def _check(self):
        flow_models = self.project_settings['models']['flow_models']
        len_flow = len(flow_models)
        if len_flow != 1:
            raise ValueError(
                f'Only one flow model can be used, found {len_flow}\n'
                f'{flow_models}'
            )
        react_models = self.project_settings['models']['reaction_models']
        len_react = len(react_models)
        if len_react != 1:
            raise ValueError(
                f'Only one reaction model can be used, found {len_react}\n'
                f'{react_models}'
            )

    def _set_path(self):
        self.mf6_path = self.project_path / 'mf6'
        self.phreeqcrm_path = self.project_path / 'phreeqcrm'
        self.rtmf6_path = self.project_path / 'rtmf6'
        self.out_path = self.project_path / 'out'
        self.internal_paths = InternalPaths(self.project_path)

    def _make_path_absolute(self):
        options = self.project_settings['phreeqcrm']
        for entry in ['database', 'chemistry_name']:
            options[entry] = self.project_path / options[entry]
        for cat in self.phreeqcrm_cell_value_categories:
            if cat in self.project_settings:
                for entry in self.project_settings[cat]:
                    if entry:
                        entry['file_name'] = (
                            self.project_path / entry['file_name']
                        )
        phr_config = self.project_settings['phreeqcrm']
        for name in [
            'pre_yaml_file',
            'post_yaml_file',
            'intermediate_model_yaml_file',
            'model_yaml_file',
        ]:
            if name in phr_config:
                phr_config[name] = self.project_path / phr_config[name]
        if 'intermediate_model_yaml_file' not in phr_config:
            phr_config['intermediate_model_yaml_file'] = (
                self.phreeqcrm_path / '_intermediate.yaml'
            )


class InternalPaths:
    """Internal paths for data manipulation.

    These paths are not intended to be modified by the model user.
    They contain data that rtmf6 generates
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, project_path, create=True):
        self.base = project_path / '.internal'
        work_path = self.base / 'work'
        self.component_models_path = self.base / 'component_models'
        self.work_path_flopy = work_path / 'flopy'
        self.work_path_phreeqcrm = work_path / 'phreeqcrm'
        self.work_path_nam = work_path / 'nam'
        if create:
            self._make_directory_structure()

    def _make_directory_structure(self):
        """Create directory tree for internal data."""
        self.component_models_path.mkdir(exist_ok=True, parents=True)
        self.work_path_flopy.mkdir(exist_ok=True, parents=True)
        self.work_path_phreeqcrm.mkdir(exist_ok=True, parents=True)
        self.work_path_nam.mkdir(exist_ok=True, parents=True)
