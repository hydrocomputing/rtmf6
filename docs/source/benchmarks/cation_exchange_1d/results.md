# Results

The results are saved in component models in MODFLOW 6 format.
For example the results for `Ca` are in the directory
`.internal/component_models/Ca` relative to the root folder.

Comparing the concentration over time ate the last cells with the
corresponding PHT3D calculation shows good agreement.

```{figure} result_advect.svg
:alt: Comparison of rtmf6 and PHT3D
:align: center

Comparison of rtmf6 and PHT3D for 1D cation exchange
```
