"""
Modify an existing simulation.

The calls SImulation allows to clone all input files and modify selected
input values.
"""

from copy import deepcopy
from pathlib import Path

import flopy

import pymf6

from rtmf6.config import Config
from rtmf6.preprocessing.adjust_prefixes import prefix_all


class Simulation:
    """Existing MF6 simulation."""

    def __init__(
        self,
        config,
        model_path=None,
        exe_name=None,
        sim=None,
        verbosity_level=0,
    ):
        self.config = config
        self._set_paths()
        if model_path is None:
            self.model_path = config.mf6_path
        self.model_name = config.project_name
        if exe_name is None:
            exe_name = exe_name = pymf6.__mf6_exe__
        if sim:
            self._sim = sim
        else:
            self._sim = flopy.mf6.MFSimulation.load(
                sim_ws=self.model_path,
                exe_name=exe_name,
                verbosity_level=verbosity_level,
            )
        self.models = {}
        for name, model in self._sim.model_dict.items():
            self.models.setdefault(model.model_type, []).append(model)
        self.needed_files = None

    def _set_paths(self):
        self.inputs_path = self.config.internal_paths.inputs_path
        self.component_models_path = self.config.internal_paths.component_models_path
        self.work_path_flopy = self.config.internal_paths.work_path_flopy
        self.work_path_mf6 = self.config.internal_paths.work_path_mf6

    def __getattr__(self, name):
        return getattr(self._sim, name)

    def clone_model(self, new_sim_path):
        """Clone a simulation."""
        new_sim = deepcopy(self._sim)
        new_sim.set_sim_path(new_sim_path)
        return self.__class__(
            config=self.config,
            model_path=new_sim_path,
            sim=new_sim,
        )

    def clone_base_model(self, skip=None):
        """Clone the base model."""
        for new_sim_path in [self.inputs_path, self.work_path_flopy]:
            new_sim = self.clone_model(new_sim_path=new_sim_path)
            new_sim.write_back()
        self.needed_files = prefix_all(self.inputs_path / 'mfsim.nam', skip=skip)

    def clone_component_model(self, component):
        """Clone a component model."""
        return self.clone_model(new_sim_path=self.component_models_path / component)

    def set_const_init_conc(self, value):
        """Set a constant concentration value."""
        transport = self.models['transport']
        const_conc = transport.get_package('ic').data_list[-1]
        const_conc.set_data(value)

    def get_stress_period_data(self, model_type, package_name):
        """Get stress period dat for a package."""
        package = self.models[model_type].get_package(package_name)
        return package.stress_period_data.data

    def set_stress_period_data(self, model_type, package_name, data):
        """Set stress period dat for a package."""
        package = self.models[model_type].get_package(package_name)
        package.stress_period_data.set_data(data)

    def write_back(self):
        """Write the modifies input data back."""
        target_path = Path(self._sim.sim_path)
        target_path.mkdir(exist_ok=True)
        self._sim.write_simulation()
