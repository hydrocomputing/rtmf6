"""Configuration."""

from pathlib import Path
import tomllib


class Config:
    """Configure a project."""

    def __init__(self, project_toml):
        with open(project_toml, 'rb') as fobj:
            self.project_settings = tomllib.load(fobj)
        self.project_name = self.project_settings['project']['name']
        self.project_path = Path(project_toml).parent / self.project_settings['project']['directory']
        self._set_path()
        self._make_path_absolute()

    def _set_path(self):
        self.mf6_path = self.project_path / 'mf6'
        self.phreeqcrm_path = self.project_path / 'phreeqcrm'
        self.rtmf6_path = self.project_path / 'rtmf6'
        self.internal_paths = InternalPaths(self.project_path)

    def _make_path_absolute(self):
        options = self.project_settings['phreeqcrm']
        for entry in ['database', 'chemistry_name']:
            options[entry] = self.project_path / options[entry]



class InternalPaths:
    """Internal paths for data manipulation.

    These paths are not intended to be modified by the model user.
    They contain data that rtmf6 generates
    """

    def __init__(self, project_path, create=True):
        self.base = project_path / '.internal'
        base_model = self.base /  'base_model'
        work_path = self.base / 'work'
        self.inputs_path = base_model / 'common_inputs'
        self.component_models_path = self.base / 'component_models'
        self.work_path_flopy = work_path / 'flopy'
        self.work_path_mf6 = work_path / 'mf6'
        self.work_path_phreeqcrm = work_path / 'phreeqcrm'
        if create:
            self._make_directory_structure()

    def _make_directory_structure(self):
        """Create directory tree for internal data."""
        self.inputs_path.mkdir(exist_ok=True, parents=True)
        self.component_models_path.mkdir(exist_ok=True, parents=True)
        self.work_path_flopy.mkdir(exist_ok=True, parents=True)
        self.work_path_mf6.mkdir(exist_ok=True, parents=True)
        self.work_path_phreeqcrm.mkdir(exist_ok=True, parents=True)


class Resources():

    def __init__(self):
        self.path = Path(__file__).parent / 'resources'
        self.tdis_fast = self.path / 'fast.tdis'
