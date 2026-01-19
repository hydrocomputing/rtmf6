# Installation

## Using pip

```bash
pip install rtmf6
```

## Using conda/mamba

```bash
conda add -c hydrocomputing rtmf6
```

## Using Pixi

Add the channel `hydrocomputing` to your channels:

```toml
[workspace]
channels = ["hydrocomputing", "conda-forge"]
```

```bash
pixi add rtmf6
```

## Prerequisites

rtmf6 requires the following dependencies:

- Python >= 3.11
- MODFLOW 6
- PhreeqcRM
- pymf6
- PhreeqPy
