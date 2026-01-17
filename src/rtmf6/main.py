"""Reactive transport modeling with MODFLOW 6."""

import multiprocessing as mp
import os
import warnings
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.theme import Theme

from rtmf6.config import Config
from rtmf6.preprocessing.create_inputs import make_inputs
from rtmf6.run import run_rtmf6

# Color themes for different terminal backgrounds
THEMES = {
    "dark": Theme({
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
    }),
    "light": Theme({
        "info": "dark_blue",
        "success": "bold dark_green",
        "warning": "dark_orange3",
        "error": "bold dark_red",
    }),
}


def _get_theme_name() -> str:
    """Get the theme name from environment."""
    theme_name = os.environ.get("RTMF6_THEME", "dark").lower()
    return theme_name if theme_name in THEMES else "dark"


# Create console with the configured theme
console = Console(theme=THEMES[_get_theme_name()])


app = typer.Typer(
    name="rtmf6",
    help="A reactive transport model based on MODFLOW 6 and PhreeqcRM.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
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
        console.print("[info]Development mode active, showing deprecation warnings.[/info]")
    else:
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    console.print("[bold]rtmf6[/bold] - A reactive transport model based on MODFLOW 6 and PhreeqcRM.")
    config = Config(config_file)

    if not run_only:
        console.print("Creating input files...")
        make_inputs(config)
        if preprocess_only:
            console.print("Preprocessing only, exiting.")
            raise typer.Exit()

    console.print("Running rtmf6...")
    run_rtmf6(config, reactions=reactions)
    console.print()
    console.print("[success]rtmf6 run complete.[/success]")


def main() -> None:
    """Entry point for the CLI."""
    mp.set_start_method("spawn")
    app()


if __name__ == "__main__":
    main()
