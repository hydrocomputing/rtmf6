"""Create needed Flopy data."""

from copy import deepcopy
from pathlib import Path
from shutil import copyfile,rmtree

import flopy
from flopy.mf6.mfbase import ExtFileAction, MFDataException
import numpy as np

from rtmf6.preprocessing.phreeqc_setup import PhreeqcRMSetup

class FlopyWorker:

    def __init__(self, config):
        self.project_name = config.project_settings['project']['name']
        self.mf6_path = config.mf6_path
        self.component_models_path = config.internal_paths.component_models_path
        self.work_path = config.internal_paths.work_path_flopy
        self.work_components_path = self.work_path / 'component_models'
        if self.work_components_path.exists():
            rmtree(self.work_components_path)
        self.work_components_path.mkdir()
        self.solution_mapping = PhreeqcRMSetup(config).solution_mapping
        init_concs_config = config.project_settings['initial_concentrations']
        bc_concs_config = config.project_settings['bc_concentrations']
        bc_types = list({entry['bc_type'] for entry in bc_concs_config})
        self.load_only = bc_types + ['ic']
        self.sim = self._load_initial_sim()
        self.write_simulation()
        self._make_init_concs(init_concs_config)
        self._make_bc_concs(bc_concs_config)
        self._make_modified_file_names(config.project_path)

    def _make_modified_file_names(self, project_path):
        self.modified_input_files = [
            project_path / package.file_path for package
            in self.init_concs + self.bc_concs]
        for src in self.modified_input_files:
            dst = self.work_path / src.name
            copyfile(src, dst)

    def _make_init_concs(self, init_concs_config):
        self.init_concs = []
        for init_conc in init_concs_config:
            self.init_concs.append(InititalConc(
                config_data=init_conc,
                solution_mapping=self.solution_mapping))

    def _make_bc_concs(self, bc_concs_config):
        self.bc_concs = []
        for bc_conc in bc_concs_config:
            self.bc_concs.append(BCConc(
                config_data=bc_conc,
                solution_mapping=self.solution_mapping))

    def _load_sim(self, sim_path):
        return flopy.mf6.MFSimulation.load(
            sim_ws=sim_path,
            sim_name=self.project_name,
            load_only=self.load_only,
            verbosity_level=0,
            lazy_io=True)

    def _load_initial_sim(self):
        sim = self._load_sim(sim_path=self.mf6_path)
        sim.set_sim_path(self.work_path)
        return sim

    def load_simulation(self):
        """Load a simulation from work path."""
        self.sim = self._load_sim(sim_path=self.work_path)

    def write_simulation(self):
        """Write simulation data back."""
        self.sim.write_simulation(
            ext_file_action=ExtFileAction.copy_none,
            silent=True
            )

    def update(self, conc_names):
        """Update concentration values for one specie."""
        for conc_name in conc_names:
            target_path = self.component_models_path / conc_name
            target_path.mkdir(exist_ok=True)
            for bc_conc in self.bc_concs:
                bc_conc.update(self.sim, conc_name)
                src = self.work_path / bc_conc.file_name
                dst = target_path / bc_conc.file_name
                copyfile(src, dst)
            for init_conc in self.init_concs:
                init_conc.update(self.sim, conc_name)
                src = self.work_path / init_conc.file_name
                dst = target_path / init_conc.file_name
                copyfile(src, dst)
            new_sim_path = self.work_components_path / conc_name
            new_sim_path.mkdir(exist_ok=True)
            self.sim.set_sim_path(new_sim_path)
            self.write_simulation()
            self.load_simulation()

    def update_all(self, keep_tracer=True, tracer_name='Tracer', skip=None):
        if skip is None:
            skip = {'H2O'}
        else:
            skip = set(skip)
        if not keep_tracer:
            skip.add(tracer_name)
        specie_names = [name for name in self.solution_mapping[0].keys()
                        if name not in skip]
        self.update(specie_names)

    def get_sol_numbers(self, file):
        """Get distribution of solution numbers."""


class InititalConc:

    def __init__(self, config_data, solution_mapping):
        """One initial concentration."""
        self.solution_mapping = solution_mapping
        self.model_name = config_data['model_name']
        self.file_path = Path(config_data['file_name'])
        self.file_name = self.file_path.name

    def update(self, sim, conc_name):
        """Update the initial concentration."""
        init = sim.get_model(self.model_name).get_package('ic')
        strt = init.strt
        try:
            # keep constant value if possible
            sol_number_float = round(strt._get_storage_obj().get_const_val(), 8)
            sol_number = int(sol_number_float)
            assert sol_number == sol_number_float, (conc_name, sol_number, sol_number_float)
            init.strt.set_data(self.solution_mapping[sol_number][conc_name])
        except MFDataException:
            sol_numbers_float = strt.data.flatten()
            sol_numbers = sol_numbers_float.astype(int)
            assert np.allclose(sol_numbers, sol_numbers_float), sol_numbers - sol_numbers_float
            conc = [self.solution_mapping[sol_number][conc_name]
                    for sol_number in sol_numbers]
            init.strt.set_data(conc)


class BCConc:

    def __init__(self, config_data, solution_mapping):
        """One bc concentration."""
        self.solution_mapping = solution_mapping
        self.model_name = config_data['model_name']
        self.bc_type = config_data['bc_type']
        self.file_path = Path(config_data['file_name'])
        self.file_name = self.file_path.name
        self.src = config_data['src']
        self.dst = config_data['dst']

    def update(self, sim, conc_name):
        """Update the stress period data.

        Solution numbers are replaced by concentration values.
        """
        bc = sim.get_model(self.model_name).get_package(self.bc_type)
        modified = {}
        for period_no, period_data in bc.stress_period_data.data.items():
            conc = []
            sol_numbers_float = period_data[self.src].flatten()
            sol_numbers = sol_numbers_float.astype(int)
            assert np.allclose(sol_numbers, sol_numbers_float), sol_numbers - sol_numbers_float
            for sol_number in sol_numbers:
                if sol_number == -1:
                    conc.append(0)
                else:
                    conc.append(self.solution_mapping[sol_number][conc_name])
            period_data[self.dst][:] = conc
            modified[period_no] = period_data
        bc.stress_period_data.set_data(modified)
