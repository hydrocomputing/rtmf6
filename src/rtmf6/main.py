"""Reactive transport modeling with MODFLOW 6."""

import multiprocessing as mp
import warnings
from pathlib import Path
from typing import Annotated, Optional

import typer

from rtmf6.config import Config
from rtmf6.preprocessing.create_inputs import make_inputs
from rtmf6.run import run_rtmf6

app = typer.Typer(
    name="rtmf6",
    help="A reactive transport model based on MODFLOW 6 and PhreeqcRM.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def run(
    config_file: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to the configuration file. Defaults to 'rtmf6.toml' in the current directory.",
        ),
    ] = None,
    no_reactions: Annotated[
        bool,
        typer.Option("-n", "--no-reactions", help="Disable chemical reactions."),
    ] = False,
    develop: Annotated[
        bool,
        typer.Option("-d", "--develop", help="Enable development mode (show deprecation warnings)."),
    ] = False,
    preprocess_only: Annotated[
        bool,
        typer.Option("-p", "--preprocess-only", help="Only create input files, do not run the model."),
    ] = False,
    run_only: Annotated[
        bool,
        typer.Option("-r", "--run-only", help="Skip preprocessing, run the model only."),
    ] = False,
) -> None:
    """Run the rtmf6 model."""
    if preprocess_only and run_only:
        raise typer.BadParameter("--preprocess-only and --run-only cannot both be specified.")

    if config_file is None:
        config_file = Path("rtmf6.toml")

    if not config_file.exists():
        raise typer.BadParameter(f"Configuration file not found: {config_file}")

    reactions = not no_reactions

    if develop:
        print("Development mode active, showing deprecation warnings.")
    else:
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    print("rtmf6 - A reactive transport model based on MODFLOW 6 and PhreeqcRM.")
    config = Config(config_file)

    if not run_only:
        print("Creating input files...")
        make_inputs(config)
        if preprocess_only:
            print("Preprocessing only, exiting.")
            raise typer.Exit()

    print("Running rtmf6...")
    run_rtmf6(config, reactions=reactions)
    print()
    print("rtmf6 run complete.")


def main() -> None:
    """Entry point for the CLI."""
    mp.set_start_method("spawn")
    app()


if __name__ == "__main__":
    main()
