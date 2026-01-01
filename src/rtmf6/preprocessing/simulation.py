"""
Modify an existing simulation.

The calls SImulation allows to clone all input files and modify selected
input values.
"""

from copy import deepcopy
from pathlib import Path

import flopy

import pymf6


class Simulation:
    """Existing MF6 simulation."""

    def __init__(
        self,
        model_path,
        model_name=None,
        exe_name=None,
        sim=None,
        verbosity_level=0,
    ):
        self.model_path = model_path
        if model_name is None:
            self.model_name = model_path.name
        else:
            self.model_name = model_name
        if exe_name is None:
            exe_name = exe_name = pymf6.__mf6_exe__
        self._model_suffixes = pymf6.__model_prefixes__
        if sim:
            self._sim = sim
        else:
            self._sim = flopy.mf6.MFSimulation.load(
                sim_ws=model_path,
                exe_name=exe_name,
                verbosity_level=verbosity_level,
            )
        self.models = {}
        for model_type in ['flow', 'transport', 'energy']:
            model = self._sim.get_model(
                f'{self._model_suffixes[model_type]}{self.model_name}'
            )
            if model:
                self.models[model_type] = model

    def __getattr__(self, name):
        return getattr(self._sim, name)

    def clone(
            self, component, component_models_path='component_models'):
        """Clone a simulation."""
        new_sim_path = self.model_path.parent / component_models_path / component
        new_sim = deepcopy(self._sim)
        new_sim.set_sim_path(new_sim_path)
        return Simulation(
            model_path=new_sim_path, model_name=self.model_name, sim=new_sim
        )

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
