# Cation Exchange 1D

This example is from PHREEQC-3 documentation {cite}`parkhurst2013phreeqc`.

```{epigraph}
The following example simulates the chemical composition of the effluent from a column containing a
cation exchanger {cite}`appelo2005geochemistry` Initially, the column contains a sodium-potassium-nitrate
solution in equilibrium with the exchanger. The column is flushed with three pore volumes of calcium
chloride solution. Calcium, potassium, and sodium react to equilibrium with the exchanger at all times. The
problem is run two ways—by using the ADVECTION data block, which models only advection, and by
using the TRANSPORT data block, which simulates advection and dispersive mixing.
```

```{figure} example11.svg
:alt: Schematic for example 11
:align: center

Schematic for example 11 in {cite:t}`parkhurst2013phreeqc`
```

## Work flow

1. {doc}`MakeMF6Model` (uses FloPy but could be done with any GUI tool that
   supports the creation of MODFLOW 6 flow and transport models)
2. {doc}`rtmf6_toml`
3. {doc}`phreeqc_input`
4. {doc}`assign_solutions`
5. {doc}`run_rtmf6`
6. Look at the {doc}`results`


```{toctree}
:maxdepth: 2
:hidden:

MakeMF6Model
rtmf6_toml
phreeqc_input
assign_solutions
run_rtmf6
results
```