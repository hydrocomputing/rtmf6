"""Create needed PhreeqcRM data."""

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
        self._make_intermediate_yaml_file()
        phreeqcrm_model = PhreeqcRMModel(str(self.intermediate_yaml_file))
        return {number: phreeqcrm_model.get_initial_concentrations(number)
                for number in self._get_solution_numbers()}

    def _make_intermediate_yaml_file(self):
        nxyz = 1
        yrm = phreeqcrm.YAMLPhreeqcRM()
        yrm.YAMLSetGridCellCount(nxyz)
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