"""Create needed PhreeqcRM data."""

import os
from pathlib import Path
from shutil import copyfile
import warnings

# PhreeqcRM gives deprecation warnings that we usually want to ignore
# Show DeprecationWarning if RTMF6_DEBUG is set to a true value
if not os.environ.get("RTMF6_DEBUG", 'False').lower() in ('true', '1', 't'):
    warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
import phreeqcrm

from phreeqpy.phreeqcrm.rm_model import PhreeqcRMModel


class PhreeqcRMSetup:

    def __init__(self, config):
        phreeqcrm_settings = config.project_settings['phreeqcrm']
        self.intermediate_yaml_file = config.internal_paths.work_path_phreeqcrm / 'intermediate.yaml'
        self.model_yaml_file = config.internal_paths.work_path_phreeqcrm / 'model.yaml'
        self.database = str(phreeqcrm_settings['database'])
        self.chemistry_name = str(phreeqcrm_settings['chemistry_name'])


    def _get_solution_numbers(self):
        """Get solution numbers.
        """
        with open(self.chemistry_name, encoding='utf-8') as fobj:
            sol_numbers = []
            for line in fobj:
                if line.lstrip().lower().startswith('solution'):
                    sol_numbers.append(int(line.split()[1]))
        sol_numbers.sort()
        return sol_numbers

    @property
    def solution_mapping(self):
        """Mapping of solution number to concentratiions."""
        self._make_intermediate_yaml_file()
        phreeqcrm_model = PhreeqcRMModel(str(self.intermediate_yaml_file))
        return {number: phreeqcrm_model.get_initial_concentrations(number)
                for number in self._get_solution_numbers()}

    def _make_intermediate_yaml_file(self):
        """Create YAML file for preprocessing."""
        nxyz = 1
        yrm = phreeqcrm.YAMLPhreeqcRM()
        yrm.YAMLSetGridCellCount(nxyz)
        _set_yaml_basics(yrm)
        yrm.YAMLLoadDatabase(self.database)
        yrm.YAMLRunFile(
            workers=True,
            initial_phreeqc=True,
            utility=True,
            chemistry_name=self.chemistry_name)
        yrm.YAMLFindComponents()
        initial_solutions = [1] * nxyz
        yrm.YAMLInitialSolutions2Module(initial_solutions)
        yrm.WriteYAMLDoc(self.intermediate_yaml_file)


class PhreeqcCellMappings:

    def __init__(self, config, flopy_worker):
        self.config = config
        self.reaction_models = config.project_settings['models']['reaction_models']
        self.flopy_worker = flopy_worker
        self.phreeqcrm_cell_value_categories = list(config.phreeqcrm_cell_value_categories.keys())

    def make_mappings(self):
        """Create mappings of solution numbers and concentrations per conc."""
        mappings = {}
        for cat in self.phreeqcrm_cell_value_categories:
            entry = self.config.project_settings[cat]
            if not entry[0]:
                mappings[cat] = None
                continue
            mappings[cat] = PhreeqcCells(entry[0], worker=self.flopy_worker).get_cells()
        return mappings


class PhreeqcCells:

    def __init__(self, config_data, worker):
        self.worker = worker
        self.model_name = config_data['model_name']
        self.file_name = config_data['file_name']
        self.start_time = config_data.get('start_time', 0)

    def get_cells(self):
        init = self.worker.sim.get_model(self.model_name).get_package('ic')
        src = self.file_name
        dst = Path(init.get_file_path())
        copyfile(src, dst)
        self.worker.load_simulation()
        init = self.worker.sim.get_model(self.model_name).get_package('ic')
        if self.worker.all_cells_active:
            float_indices = init.strt.data.flatten()
        else:
            float_indices = init.strt.data.flatten()[self.worker.active_cells]
        indices = float_indices.astype(int)
        if len(indices) != self.worker.nxyz:
            raise ValueError(
                'Number of cells in PhreeqcCRM mapping does not match number of active cells in MF6\n'
                f'found {len(indices)=} and {self.worker.nxyz=}'
            )
        assert np.allclose(indices, float_indices), indices - float_indices
        return indices


class YAMLCreator:

    def __init__(self, config, cell_mappings, nxyz):
        self.phr_config = config.project_settings['phreeqcrm']
        self.cell_mappings = cell_mappings
        self.nxyz = nxyz
        self.set_error_mode()
        self.phreeqcrm_cell_value_categories = config.phreeqcrm_cell_value_categories

    def set_error_mode(self, error_handler='error_code'):
        error_options = {
            'error_code': 0,
            'cpp_exception': 1,
            'graceful_exit': 2
        }
        if error_handler not in error_options:
            msg = f'error_handle needs to be one off {", ".join(error_options)}'
            raise ValueError(msg)
        self.error_handler = error_options[error_handler]

    def _create_yaml(self):
        """Create model yaml file."""
        yrm = phreeqcrm.YAMLPhreeqcRM()
        yrm.YAMLThreadCount(self.phr_config['number_of_threads'])
        yrm.YAMLSetGridCellCount(self.nxyz)
        yrm.YAMLSetErrorHandlerMode(self.error_handler)
        _set_yaml_basics(yrm)
        # Set conversion from seconds to user units (days) Only affects one print statement
        time_conversion = 1.0 / 86400.0
        yrm.YAMLSetTimeConversion(time_conversion)
        ones_int = np.ones(self.nxyz, dtype=int)
        ones_float = np.ones(self.nxyz)
        # Set representative volume
        yrm.YAMLSetRepresentativeVolume(ones_float)
        # Set initial density
        yrm.YAMLSetDensityUser(ones_float)
        # Porosity handel by MF6
        yrm.YAMLSetPorosity(ones_float)
        # Set initial saturation
        yrm.YAMLSetSaturationUser(ones_int)
        # Load database
        yrm.YAMLLoadDatabase(str(self.phr_config['database']))
        # Run file to define solutions and reactants for initial conditions, selected output
        workers = True             # Worker instances do the reaction calculations for transport
        initial_phreeqc = True     # InitialPhreeqc instance accumulates initial and boundary conditions
        utility = True             # Utility instance is available for processing
        yrm.YAMLRunFile(
            workers,
            initial_phreeqc,
            utility,
            str(self.phr_config['chemistry_name'])
            )

        # Clear contents of workers and utility
        initial_phreeqc = False
        input = "DELETE; -all"
        yrm.YAMLRunString(workers, initial_phreeqc, utility, input)
        yrm.YAMLAddOutputVars("AddOutputVars", "true")

        # Determine number of components to transport
        yrm.YAMLFindComponents()
        for mapping_name, values in self.cell_mappings.items():
            if values is not None:
                func = getattr(yrm, self.phreeqcrm_cell_value_categories[mapping_name])
                func(values)
        # Write YAML file
        yaml_file = self.phr_config['intermediate_model_yaml_file']
        yrm.WriteYAMLDoc(str(yaml_file))
        return yaml_file.read_text().rstrip() + '\n'

    def make_phreeqcrm_yaml(self):
        """Create the model YAML file with pre and post parts."""
        pre_yaml = self.phr_config.get('pre_yaml_file')
        yaml = ''
        if pre_yaml:
            yaml += '# pre yaml start\n'
            yaml += pre_yaml.read_text().rstrip()
            yaml += '\n# pre yaml end\n'
        post_yaml = self.phr_config.get('post_yaml_file')
        yaml += self._create_yaml()
        if post_yaml:
            yaml += '# post yaml start\n'
            yaml += pre_yaml.read_text().rstrip()
            yaml += '\n# post yaml end\n'
        out = self.phr_config['model_yaml_file']
        out.write_text(yaml)


def _set_yaml_basics(yrm):
    """Set basic YAMl options."""
    yrm.YAMLSetComponentH2O(False)
    yrm.YAMLSetRebalanceFraction(0.5)
    yrm.YAMLSetRebalanceByCell(True)
    yrm.YAMLUseSolutionDensityVolume(False)
    yrm.YAMLSetPartitionUZSolids(False)

    # Set concentration units
    # 1, mg/L; 2, mol/L; 3, kg/kgs
    yrm.YAMLSetUnitsSolution(2)
    # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsPPassemblage(1)
    yrm.YAMLSetUnitsExchange(1)
    yrm.YAMLSetUnitsSurface(1)
    yrm.YAMLSetUnitsGasPhase(1)
    yrm.YAMLSetUnitsSSassemblage(1)
    yrm.YAMLSetUnitsKinetics(1)
