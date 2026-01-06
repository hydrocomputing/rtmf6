"""Create needed Flopy data."""

from copy import deepcopy
from pathlib import Path

import flopy
from flopy.mf6.mfbase import ExtFileAction

from rtmf6.preprocessing.phreeqc_setup import PhreeqcRMSetup

class FlopyWorker:

    def __init__(self, config):
        self.project_name = config.project_settings['project']['name']
        self.mf6_path = config.mf6_path
        self.work_path = config.internal_paths.work_path_flopy
        self.solution_mapping = PhreeqcRMSetup(config).solution_mapping
        bc_concs_config = config.project_settings['bc_concentrations']
        bc_types = list({entry['bc_type'] for entry in bc_concs_config})
        self.load_only = bc_types + ['ic']
        self.sim = self._load_initial_sim()
        self.write_simulation()
        self._make_bc_conc(bc_concs_config)

    def _make_bc_conc(self, bc_concs_config):
        self.bc_concs = []
        for bc_conc in bc_concs_config:
            self.bc_concs.append(BCConc(
                sim=self.sim,
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
            new_sim_path = self.work_path / conc_name
            new_sim_path.mkdir(exist_ok=True)
            self.sim.set_sim_path(new_sim_path)
            for bc_conc in self.bc_concs:
                bc_conc.update(conc_name)
            self.write_simulation()
            self.load_simulation()


class BCConc:

    def __init__(self, sim, config_data, solution_mapping):
        """One bc concnetration."""
        self.sim = sim
        self.solution_mapping = solution_mapping
        self.model_name = config_data['model_name']
        self.bc_type = config_data['bc_type']
        self.file_name = config_data['file_name']
        self.src = config_data['src']
        self.dst = config_data['dst']

    def update(self, conc_name):
        """Update the stress period data.

        Solution numbers are replaced by concentration values.
        """
        bc = self.sim.get_model(self.model_name).get_package(self.bc_type)
        modified = {}
        for period_no, period_data in bc.stress_period_data.data.items():
            conc = []
            for sol_number in period_data[self.src]:
                if sol_number == -1:
                    conc.append(0)
                else:
                    conc.append(self.solution_mapping[sol_number][conc_name])
            period_data[self.dst][:] = conc
            modified[period_no] = period_data
        bc.stress_period_data.set_data(modified)
