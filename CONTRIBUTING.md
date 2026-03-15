# Contributing to rtmf6

Contributions to tmf6 are welcome.
This document describes how to contribute to rtmf6.

## Forking

The best way to contribute is to fork a repository. This [description](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) explains how to fork a repository.
After adding your code, you contribute your changes with a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
[Collaborating with pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests) provides a comprehensive guide.

## Branch model

All development is done in branches. Following this [branch model](https://gist.github.com/Wayne-Jones/d2adf16637121a34baa53e6ae3ca049f#file-branchmodel-md), we use these types of branches:

Instance        | Branch                     | Description, Instructions, Notes
--------------- | -------------------------- | --------------------------------
Stable          | `main`                     | Accepts merges from Working and Hotfixes
Working         | `develop`                  | Accepts merges from Features/Issues and Hotfixes
Features/Issues | `feature/my-new-feature`   | Always branch off HEAD of Working
Hotfix          | `hotfix/fix-something-bad` | Always branch off master

The default branch is `develop`. The branch `main` is only used to release a new version. All development happens in feature branches, e.g. `feature/dynamic-time-stepping` that will be merged into developed via a pull request.

## Branch naming

The naming of branches is based on this [article](https://medium.com/@abhay.pixolo/naming-conventions-for-git-branches-a-cheatsheet-8549feca2534).

### Basic Rules

Only use `lowercase-hyphen-separated` names with alphanumeric characters (a-z, A-Z, 0–9) and one hyphen between words. Use descriptive names and limit the use of numbers.

### Branch Prefixes

Branch prefixes help to identify the purpose of a branch. We use these prefixes:

* **Feature branch:** Develop a new feature. Example: `feature/rb-heat-river`.
* **Bugfix Branch:** Fix a bug. Example: `bugfix/solver-parameter-defaults`.
* **Hotfix Branch:** Fix a critical bug that will be directly merged into `main`. Example: `hotfix/output-deleted-by-accident`.
* **Release branch:** Prepare a new production release. Example: `release/0.5.1`.
* **Documentation branch:** Write, update, or fix documentation. Example: `docs/tutorial-unstructured-grid`
* **Benchmark branch:** Add or modify a benchmark. Example: `benchmark/appelo-2015-slow-kinetics`

## Adding a benchmark

Benchmarks use `rtmf6` for example models. The workflow typically doesn't involve modifying the Python source code. This means running `rtmf6` can be done with released version instead of the code in the branch `develop`. The documentation needs mor setup. The easiest way is to use [Pixi](https://pixi.prefix.dev/dev/). The command `pixi shell -e docs` will install all needed libraries. Now `rtmf6 -V` should show the version.

The benchmark should be located in `benchmarks/my-benchmark` (replace `my-benchmark` with your benchmark name). The layout should follow this form:

```
benchmarks/my-benchmark
├── description
│   └── my_benchmark_explained.md
├── model
│   ├── mf6
│   │   ├── ex10_simple.gwfgwt
│   │   ├── ex10_simple.tdis
...
│   │   └── mfsim.nam
│   ├── phreeqcrm
│   │   ├── phreeqc_code.pqi
│   │   ├── phreeqc.dat
│   │   └── post.yaml
│   ├── postprocessing
│   │   ├── postprocess_my_benchmark.py
│   │   └── plot.py
│   ├── preprocessing
│   │   └── create_my_bnenchmark.py
│   ├── rtmf6
│   │   ├── init_conc.ic
│   │   ├── init_equilibrium_phases.ic
│   │   └── init_kinetics.ic
│   └── rtmf6.toml
└── results
    └── my_benchmark.png
```

Additional sub-directories maybe useful.

### Writing benchmark documentation

The documentation is build with Sphinx. Add new directory `docs/source/benchmarks/my-benchmark` (replace `my-benchmark` with your benchmark name). The documentation excepts Markdown files and Jupyter Notebooks.
The command `pixi run docs-build` will build the documentation in `docs/_build/html`.
