# rtmf6 - Reactive Transport Modeling with MODFLOW 6 and PHREEQC 3

rtmf6 provides a Python interface for coupling MODFLOW 6 groundwater
flow simulations with PHREEQC reactive transport modeling.

## Features

- Seamless integration of MODFLOW 6 and PhreeqcRM
- Strives to support all MODFLOW 6 and PHREEQC feature
- Minimal coupling configuration
- Parallel execution of transport and geochemical calculations
- Support for complex geochemical reactions
- Powerful commandline interface (CLI)

## Principles

rtmf6 creates a separate MODFLOW 6 model for each reactive model species.
Let's call these models component models.
rtmf6 manages all component models internally.
The user works with one model, even though internally 10, 20 or flow and
transport models exist.
All initial concentration and concentration at boundary conditions of MODFLOW 6
are defined as solutions numbers.
These solution numbers are the solution numbers in the PHREEQC input file.
Going with PhreeqRM conventions these files use the extension `.pqi`.
They are valid PHREEQC input files that provide all concentration data.
The user provides the spatial distribution of these solutions numbers with
MODFLOW 6.
rtmf6 uses this information and creates input files with concentrations for
all models.

All flow and transport models run in parallel by default.
This means the MODFLOW calculation uses as many processes as the number
species.
Note that Oxygen and Hydrogen are also modeled,
increasing the model number.
Provided the computer has at least as many (perfomance) cores as processes
start by rtmf6,
all MODFLOW calculation will happen in parallel.
In addition, the PHREEQC calculation can also be run parallel by specify the
number of threads used for PhreeqcRM.

rtmf6 strives to use MODFLOW 6 and PHREEQC input files as much as possible,
adding only the minium of rtmf6-specific configuration.
This allows to use established tools for large parts of the preprocessing.

## General Workflow

1. Create you MODFLOW 6 transport model
2. Create a TOML config file
3. Define PHREEQC solutions for initial boundary conditions
4. Assign solutions to MODFLOW 6 cells with native input file syntax
5. Run `rtmf6`

The [documentation](https://docs.rtmf6.com/) provides more details.
