"""Configuration."""

from pathlib import Path


class Config:
    """Configure a project."""

    def __init__(self, project_path, project_name='rtmf6sim'):
        self.project_path = Path(project_path)
        self.project_name = project_name
        self.mf6_path = self.project_path / 'mf6'
        self.phreeqcrm_path = self.project_path / 'phreeqcrm'
        self.rtmf6_path = self.project_path / 'rtmf6'
        self.internal_paths = InternalPaths(self.project_path)


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
        if create:
            self._make_directory_structure()

    def _make_directory_structure(self):
        """Create directory tree for internal data."""
        self.inputs_path.mkdir(exist_ok=True, parents=True)
        self.component_models_path.mkdir(exist_ok=True, parents=True)
        self.work_path_flopy.mkdir(exist_ok=True, parents=True)
        self.work_path_mf6.mkdir(exist_ok=True, parents=True)


class Resources():

    def __init__(self):
        self.path = Path(__file__).parent / 'resources'
        self.tdis_fast = self.path / 'fast.tdis'
