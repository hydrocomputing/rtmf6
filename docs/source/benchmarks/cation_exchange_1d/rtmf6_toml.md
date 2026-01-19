# Create a TOML config file

Create a TOML file.

The table `[project]` specifies the project name that will bu use for all
file simulation names.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [project]
:end-before: [models]
```

The table `[models]` specifies the names of the flow and transport models
involved in the reaction calculations.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [models]
:end-before:  [[bc_concentrations]]
```

(toml-bc-conc)=
The tables `[[bc_concentrations]]` specify the solution numbers for all
boundary conditions that specify concentrations.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [[bc_concentrations]]
:end-before: [[initial_concentrations]]
```

(toml-initial-conc)=
The tables `[[initial_concentrations]]` specify the solution numbers for the
spatial distribution of initial concentrations.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [[initial_concentrations]]
:end-before: [[exchanges]]
```

The tables `[[exchanges]]` specify the solution numbers for the
spatial distribution of initial concentrations.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [[exchanges]]
:end-before: [phreeqcrm]
```

The table `[phreeqcrm]` specifies PhreeqcRM related information.
The file under `model_yaml_file` will be created by rtmf6 and can be useful for
fining input errors.

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6.toml
:language: toml
:start-at: [phreeqcrm]
```
