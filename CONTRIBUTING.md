# Contributing to rtmf6

Contributions to tmf6 are welcome.
This document describes how to contribute to rtmf6.

## Using Pixi

The project uses [Pixi](https://pixi.prefix.dev/) for environments and many tasks. It simplifies workflows considerably. Pixi is very powerful but you don't need know much about it. You only need to [install Pixi](https://pixi.prefix.dev/dev/installation/) and type in a few commands provided below. Knowing more about Pixi is useful but no prerequisite.

## Forking

The best way to contribute is to fork a repository. This [description](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) explains how to fork a repository. You only need the branch `develop`.

After adding your code, you can contribute your changes with a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork). [Collaborating with pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests) provides a comprehensive guide.

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

Sphinx doesn't allow to include files outside its root directory. Since it can be useful to include files from the benchmark directory, you specify files that will be automatically copied into the Sphinx root. Create a file `autocopy.config` that specifies the files you like to use:

```
../../../../benchmarks/Ex10_simple/model/preprocessing.ipynb
../../../../benchmarks/Ex10_simple/model/postprocessing.ipynb
../../../../benchmarks/Ex10_simple/results/PHT3D_RTMF6_compare.png
```

**Important:** Use relative paths to the directory that contains `autocopy.config`. The build process will create a new directory `.autocopy` next to `autocopy.config` and copies all specified files into it. Now, you can reference these files: `.autocopy/postprocessing.ipynb`.

### Typical workflow

A typical workflow could look like this:

1. Install git on your computer
2. Create an account on GitHub
3. Create a fork on GitHub using the button "Fork" on the top right on Github of [this repo](https://github.com/hydrocomputing/rtmf6) (see [above](#forking) for more details)
4. Clone to your local machine from your fork: `git clone https://github.com/<your.accounct>/rtmf6.git` (copy the URL from the green button with "<>Code" on the right top **in your fork** on GitHub)
5. On your local machine, make sure your are in branch `develop`: `git branch`
6. Create your branch: `git switch -c benchmark/my-benchmark` (replace `my-benchmark` with your benchmark name).
7. [Install Pixi](https://pixi.prefix.dev/dev/installation/)
8. Activate the `docs` environment: `pixi shell -e docs`
9. Add your benchmark code and try it out with `rmf6` from the directory with your `rtmf6.toml`
10. Write your benchmark documentation
11. Build the documentation: `pixi run docs-build`
12. Look at the documentation: Click on  `docs/_build/html/index.html`.
13. Commit everything: `git add file1 file2` and `git ci` (of course having multiple commits, one after each sub-step, is even better)
14. Push to your fork: `git push` gives an error message and tells you what to do to create a new branch on your fork
15. Got to your fork on Github and click on the green button that offers to create a pull request (PR) and follow the steps

Let us know if this works for you of if the items above are missing something or not clear enough.
