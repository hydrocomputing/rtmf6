"""
Modify an existing simulation.

The calls SImulation allows to clone all input files and modify selected
input values.
"""

from copy import deepcopy
from pathlib import Path
from shutil import copyfile

import flopy

import pymf6

from rtmf6.config import Config, Resources
from rtmf6.preprocessing.adjust_prefixes import prefix_all, get_model_file_names


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
        self.needed_files = prefix_all(self.inputs_path / 'mfsim.nam', skip_model_names=skip)

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


def copy_to_work_mf6(config):
    src = config.mf6_path
    dst = config.internal_paths.work_path_mf6
    mfsim_src = src / 'mfsim.nam'
    mfsim_dst = dst / 'mfsim.nam'
    copyfile(mfsim_src, mfsim_dst)
    model_file_names = get_model_file_names(mfsim_dst)
    for names in model_file_names.values():
        for name in names:
            copyfile(src / name, dst / name)
    skipped = prefix_all(
        mfsim_dst,
        simulate=False,
        skip_mfsim=['TDIS6', 'gwf6', 'gwt6'],
        skip_model_names={'gwt6': ['IC6']})
    print(skipped)
    package_names = []
    for values in skipped['needed_package_files'].values():
            for sub_value in values.values():
                package_names.extend(sub_value)
    for name in package_names:
        copyfile(src / name, dst / name)
    resources = Resources()
    tdis_file_name = skipped['tdis_file_name']
    tdis = dst / tdis_file_name
    tdis.write_text(resources.tdis_fast.read_text())
