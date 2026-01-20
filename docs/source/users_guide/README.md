# `rtmf6`

A reactive transport model based on MODFLOW 6 and PhreeqcRM.

**Usage**:

```console
$ rtmf6 [OPTIONS] [CONFIG_FILE] COMMAND [ARGS]...
```

**Arguments**:

* `[CONFIG_FILE]`: Path to the configuration file. Defaults to `rtmf6.toml` in the current directory.

**Options**:

* `-n, --no-reactions`: Disable chemical reactions.
* `-p, --preprocess-only`: Only create input files, do not run the model.
* `-r, --run-only`: Skip preprocessing, run the model only.
* `-V, --version`: Show version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `run`: Run the rtmf6 model.
* `info`: Show version and other information.
* `config`: Show configuration information.

## `rtmf6 run`

Run the rtmf6 model.

**Usage**:

```console
$ rtmf6 run [OPTIONS] [CONFIG_FILE]
```

**Arguments**:

* `[CONFIG_FILE]`: Path to the configuration file. Defaults to `rtmf6.toml` in the current directory.

**Options**:

* `-n, --no-reactions`: Disable chemical reactions.
* `-p, --preprocess-only`: Only create input files, do not run the model.
* `-r, --run-only`: Skip preprocessing, run the model only.
* `--help`: Show this message and exit.

## `rtmf6 info`

Show version and other information.

**Usage**:

```console
$ rtmf6 info [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `rtmf6 config`

Show configuration information.

**Usage**:

```console
$ rtmf6 config [OPTIONS] [CONFIG_FILE]
```

**Arguments**:

* `[CONFIG_FILE]`: Path to the configuration file. Defaults to `rtmf6.toml` in the current directory.

**Options**:

* `--help`: Show this message and exit.
