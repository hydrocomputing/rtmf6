# Installation


## Using conda/mamba

```bash
conda add -c hydrocomputing rtmf6
```

## Using Pixi

Add the channel `hydrocomputing` to your channels:

## Using pip

Not available yet.


```toml
[workspace]
channels = ["hydrocomputing", "conda-forge"]
```

```bash
pixi add rtmf6
```

## Prerequisites

You need to
[install MODFLOW 6](https://github.com/MODFLOW-ORG/modflow6/releases)
and
[configure pymf6](https://pymf6.readthedocs.io/en/latest/#configuration).
