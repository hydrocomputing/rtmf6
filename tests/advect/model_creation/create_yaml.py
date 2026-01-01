from pathlib import Path

import phreeqcrm


def create_yaml(file_name, data_path, nxyz=300, nthread=1, error_handler='error_code'):
    """Create model yaml file."""
    data_path = Path(data_path)
    error_options = {
        'error_code': 0,
        'cpp_exception': 1,
        'graceful_exit': 2
    }
    assert error_handler in error_options, f'error_handle needs to be one off {", ".join(error_options)}'
    # Create YAMLPhreeqcRM document
    yrm = phreeqcrm.YAMLPhreeqcRM()

    yrm.YAMLThreadCount(nthread)

    # Set GridCellCount
    yrm.YAMLSetGridCellCount(nxyz)

    # Set some properties
    yrm.YAMLSetErrorHandlerMode(error_options[error_handler])
    yrm.YAMLSetComponentH2O(False)
    yrm.YAMLSetRebalanceFraction(0.5)
    yrm.YAMLSetRebalanceByCell(True)
    yrm.YAMLUseSolutionDensityVolume(False)
    yrm.YAMLSetPartitionUZSolids(False)

    # Set concentration units
    yrm.YAMLSetUnitsSolution(2)           # 1, mg/L; 2, mol/L; 3, kg/kgs
    yrm.YAMLSetUnitsPPassemblage(1)       # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsExchange(1)           # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsSurface(1)            # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsGasPhase(1)           # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsSSassemblage(1)       # 0, mol/L cell; 1, mol/L water; 2 mol/L rock
    yrm.YAMLSetUnitsKinetics(1)           # 0, mol/L cell; 1, mol/L water; 2 mol/L rock

    # Set conversion from seconds to user units (days) Only affects one print statement
    time_conversion = 1.0 / 86400.0
    yrm.YAMLSetTimeConversion(time_conversion)

    # Set representative volume
    rv = [1] * nxyz
    yrm.YAMLSetRepresentativeVolume(rv)

    # Set initial density
    density = [1.0] * nxyz
    yrm.YAMLSetDensityUser(density)

    # Set initial porosity
    por = [0.2] * nxyz
    yrm.YAMLSetPorosity(por)

    # Set initial saturation
    sat = [1] * nxyz
    yrm.YAMLSetSaturationUser(sat)

    # Load database
    yrm.YAMLLoadDatabase(str(data_path / 'phreeqc.dat'))

    # Run file to define solutions and reactants for initial conditions, selected output
    workers = True             # Worker instances do the reaction calculations for transport
    initial_phreeqc = True     # InitialPhreeqc instance accumulates initial and boundary conditions
    utility = True             # Utility instance is available for processing
    yrm.YAMLRunFile(workers, initial_phreeqc, utility, str(data_path / 'advect.pqi'))

    # Clear contents of workers and utility
    initial_phreeqc = False
    input = "DELETE; -all"
    yrm.YAMLRunString(workers, initial_phreeqc, utility, input)
    yrm.YAMLAddOutputVars("AddOutputVars", "true")

    # Determine number of components to transport
    yrm.YAMLFindComponents()

    # initial solutions
    initial_solutions = [1] * nxyz
    yrm.YAMLInitialSolutions2Module(initial_solutions)

    # initial exchanges
    initial_exchanges = [1] * nxyz
    yrm.YAMLInitialExchanges2Module(initial_exchanges)

    # Write YAML file
    yrm.WriteYAMLDoc(file_name)

if __name__ == '__main__':
    for option in ['error_code', 'cpp_exception', 'graceful_exit']:
        create_yaml(
            file_name=f'advect_{option}.yaml',
            data_path='.',
            error_handler=option)
