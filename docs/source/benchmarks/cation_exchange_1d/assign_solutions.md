# Assign solutions to MODFLOW 6 cells with native input file syntax

## Boundary conditions

Modify the file `mf6/gwf_cat_ex_1d.wel` and add another auxiliary variable
`rtmf6_sol_number` in addition to `concentration` you already used in the
transport simulation:

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/mf6/gwf_cat_ex_1d.wel
:start-at: BEGIN
```

The last value `0` specifies that the solution `SOLUTION 0  CaCl2` in the file
[`advect.pqi`](#advect.pqi) is used for the boundary condition.

You need to specify this file name with relative path to the project root in
[TOML config file under `bc_concentrations`](#toml-bc-conc)

## Initial concentrations

Modify the file `mf6/gwt_cat_ex_1d.ic` and replace concentration value with
the solution number:

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/mf6/gwt_cat_ex_1d.ic
:start-at: BEGIN
```

While the value of `STRT` has a datatype of float, it will be converted into an
integer to represent an solution number in the file [`advect.pqi`](#advect.pqi).

You need to specify this file name with relative path to the project root in
 [TOML config file under `initial_concentrations`](#toml-initial-conc).

:::{note}
 You can copy the file `mf6/gwt_cat_ex_1d.ic` into a different directory first,
 modify it and specify this new paths in the TOML configuration file.
 See also: [how exchanges are specified](#specify-exchanges).
:::

(specify-exchanges)=
## Exchanges

Copy the file `mf6/gwt_cat_ex_1d.ic` to `rtmf6/init_exchanges.ic`.
Modify the file `rtmf6/init_exchanges.ic` and replace concentration value with
the solution number:

```{literalinclude} ../../../../benchmarks/cation_exchange_1d/rtmf6/rtmf6/init_exchanges.ic
:start-at: BEGIN
```
