# Installation

## Prerequisites

You need to
[install MODFLOW 6](https://github.com/MODFLOW-ORG/modflow6/releases)
and
[configure pymf6](https://pymf6.readthedocs.io/en/latest/#configuration)
You don't need to explicitly install `pymf6`.
It is a dependency of `rtmf6` and therefore will be installed automatically.
You only need to specify the path of MODFLOW 6 DLL (shared library.)

## Alternative 1: Using Pixi

### Installing Pixi

Please follow the instructions how to
[install Pixi](https://pixi.sh/latest/installation/).
After installing Pixi, the command `pixi` should be available in a
terminal window.

### Creating a Pixi workspace

You need to create a Pixi workspace.
This can be done either by typing in a terminal window:

```shell
pixi init rtmf6_project
cd rtmf6_project
```

Now the directory `rtmf6_project` contains a file named `pixi.toml` that
contains the configuration.
You need to add the channel `hydrocomputing` to your Pixi workspace.
This can be done either by typing in a terminal window:

```shell
pixi workspace channel add --prepend hydrocomputing
```

or by editing the file `pixi.toml`,
modifying the key `channels` in the section `[workspace]` from:

```toml
[workspace]
channels = ["conda-forge"]
```

to:

```toml
[workspace]
channels = ["hydrocomputing", "conda-forge"]
```

### Installing `rtmf6`

Now you can install `rtmf6` by typing:

```shell
pixi add rtmf6
```

## Alternative 2: Using Conda with Miniforge, Miniconda, or Anaconda

Alternatives to using Pixi are
[Miniforge](https://github.com/conda-forge/miniforge),
[Miniconda](https://conda.io/miniconda.html),
or [Anaconda](https://www.continuum.io/downloads).
Miniforge is a minimal conda installer with the conda-forge channel as the
default channel.

Anaconda is a Python distribution with many Python packages.
Miniconda is a much smaller version of the Anaconda Distribution with a few
packages.
Make sure the
[Anaconda license](https://docs.anaconda.com/anaconda/licenses/)
works for you before using this option.
Otherwise, use Miniforge, or our recommendation Pixi.

After installing Miniconda or Anaconda, the command `conda` should be
available in a terminal window::

```shell
conda
usage: conda [-h] [-v] [--no-plugins] [-V] COMMAND ...

conda is a tool for managing and deploying applications, environments and packages.
```

### Installing `rtmf6`

In a terminal window type:

```shell
conda config --add channels conda-forge
conda config --add channels hydrocomputing
```

Create a `conda` environment by typing:

```shell
conda create -n rtmf6_314 python=3.14
```

Answer "Yes" to the question(s) and type enter.

Next, type:

```shell
conda activate rtmf6_314
conda install rtmf6
```

## Alternative 3: Using Pip or uv

Not available yet. Coming soon.

## Test your installation

Type to check the version:

```shell
rtmf6 -V
```

Follow the steps for running the example
[Cation Exchange 1D](#cation_exchange_1d-fast-path)
to test if the simulation works.
