"""Reactive transport modeling with MODFLOW 6."""

import multiprocessing as mp
import os
from pathlib import Path
from typing import Annotated, Optional

import typer
import typer.rich_utils
from rich.console import Console
from rich.theme import Theme

from rtmf6._version import __version__
from rtmf6.config import Config
from rtmf6.preprocessing.create_inputs import make_inputs
from rtmf6.run import run_rtmf6

# Color themes for different terminal backgrounds
THEMES = {
    'dark': Theme(
        {
            'info': 'cyan',
            'success': 'bold green',
            'warning': 'yellow',
            'error': 'bold red',
        }
    ),
    'light': Theme(
        {
            'info': 'dark_blue',
            'success': 'bold dark_green',
            'warning': 'dark_orange3',
            'error': 'bold dark_red',
        }
    ),
}

# Typer help text style overrides for light theme
TYPER_STYLES_LIGHT = {
    'STYLE_OPTION': 'dark_cyan',
    'STYLE_ARGUMENT': 'dark_cyan',
    'STYLE_COMMAND': 'dark_cyan',
    'STYLE_SWITCH': 'dark_green',
    'STYLE_METAVAR': 'dark_orange3',
    'STYLE_METAVAR_SEPARATOR': 'dim',
    'STYLE_USAGE': 'dark_orange3',
    'STYLE_USAGE_COMMAND': 'bold dark_blue',
    'STYLE_HELPTEXT_FIRST_LINE': '',
    'STYLE_HELPTEXT': 'dim',
    'STYLE_OPTION_HELP': '',
    'STYLE_OPTION_DEFAULT': 'dim grey42',
    'STYLE_REQUIRED_SHORT': 'dark_red',
    'STYLE_REQUIRED_LONG': 'dim dark_red',
    'STYLE_OPTIONS_PANEL_BORDER': 'grey42',
    'STYLE_COMMANDS_PANEL_BORDER': 'grey42',
    'STYLE_ERRORS_PANEL_BORDER': 'dark_red',
}


HELP_CONFIG_FILE = 'Path to the configuration file. Defaults to `rtmf6.toml` in the current directory.'


def _get_theme_name() -> str:
    """Get the theme name from environment."""
    theme_name = os.environ.get('RTMF6_THEME', 'dark').lower()
    return theme_name if theme_name in THEMES else 'dark'


def _configure_typer_styles() -> None:
    """Configure typer help text styles based on theme."""
    if _get_theme_name() == 'light':
        for style_name, style_value in TYPER_STYLES_LIGHT.items():
            setattr(typer.rich_utils, style_name, style_value)


# Apply theme configuration at module load
_configure_typer_styles()

# Create console with the configured theme
console = Console(theme=THEMES[_get_theme_name()])


app = typer.Typer(
    name='rtmf6',
    help='A reactive transport model based on MODFLOW 6 and PhreeqcRM.',
    context_settings={'help_option_names': ['-h', '--help']},
    rich_markup_mode='rich',
)


def _run_model(
    config_file: Optional[Path],
    no_reactions: bool,
    preprocess_only: bool,
    run_only: bool,
) -> None:
    """Core logic for running the rtmf6 model."""
    if preprocess_only and run_only:
        raise typer.BadParameter(
            '--preprocess-only and --run-only cannot both be specified.'
        )

    if config_file is None:
        config_file = Path('rtmf6.toml')

    if not config_file.exists():
        raise typer.BadParameter(
            f'Configuration file not found: {config_file}'
        )

    reactions = not no_reactions

    console.print(
        '[bold]rtmf6[/bold] - A reactive transport model based on MODFLOW 6 and PhreeqcRM.'
    )
    config = Config(config_file)

    if not run_only:
        console.print('Creating input files...')
        make_inputs(config)
        if preprocess_only:
            console.print('Preprocessing only, exiting.')
            raise typer.Exit()

    console.print('Running rtmf6...')
    run_rtmf6(config, reactions=reactions)
    console.print()
    console.print('[success]rtmf6 run complete.[/success]')


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f'rtmf6 version {__version__}')
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    config_file: Annotated[
        Optional[Path],
        typer.Argument(help=HELP_CONFIG_FILE),
    ] = None,
    no_reactions: Annotated[
        bool,
        typer.Option(
            '-n', '--no-reactions', help='Disable chemical reactions.'
        ),
    ] = False,
    preprocess_only: Annotated[
        bool,
        typer.Option(
            '-p',
            '--preprocess-only',
            help='Only create input files, do not run the model.',
        ),
    ] = False,
    run_only: Annotated[
        bool,
        typer.Option(
            '-r', '--run-only', help='Skip preprocessing, run the model only.'
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            '-V',
            '--version',
            callback=_version_callback,
            is_eager=True,
            help='Show version and exit.',
        ),
    ] = False,
) -> None:
    """A reactive transport model based on MODFLOW 6 and PhreeqcRM."""
    if ctx.invoked_subcommand is not None:
        return

    # Workaround: typer parses subcommand names as config_file before recognizing them as subcommands.
    # If config_file matches a subcommand name and doesn't exist as a file, invoke that subcommand.
    if (
        config_file is not None
        and config_file.name in _SUBCOMMANDS
        and not config_file.exists()
    ):
        subcommand_name = config_file.name
        if subcommand_name == 'run':
            # Special case: run command needs parameters from callback
            ctx.invoke(
                run,
                config_file=None,
                no_reactions=no_reactions,
                preprocess_only=preprocess_only,
                run_only=run_only,
            )
        else:
            ctx.invoke(_SUBCOMMANDS[subcommand_name])
        return

    _run_model(config_file, no_reactions, preprocess_only, run_only)


@app.command()
def run(
    config_file: Annotated[
        Optional[Path],
        typer.Argument(
            help=HELP_CONFIG_FILE,
        ),
    ] = None,
    no_reactions: Annotated[
        bool,
        typer.Option(
            '-n', '--no-reactions', help='Disable chemical reactions.'
        ),
    ] = False,
    preprocess_only: Annotated[
        bool,
        typer.Option(
            '-p',
            '--preprocess-only',
            help='Only create input files, do not run the model.',
        ),
    ] = False,
    run_only: Annotated[
        bool,
        typer.Option(
            '-r', '--run-only', help='Skip preprocessing, run the model only.'
        ),
    ] = False,
) -> None:
    """Run the rtmf6 model."""
    _run_model(config_file, no_reactions, preprocess_only, run_only)


@app.command()
def info() -> None:
    """Show version and other information."""
    console.print(f'[bold]rtmf6[/bold] version {__version__}')


@app.command('config')
def config_cmd(
    config_file: Annotated[
        Optional[Path],
        typer.Argument(
            help=HELP_CONFIG_FILE,
        ),
    ] = None,
) -> None:
    """Show configuration information."""
    if config_file is None:
        config_file = Path('rtmf6.toml')

    if not config_file.exists():
        raise typer.BadParameter(
            f'Configuration file not found: {config_file}'
        )

    cfg = Config(config_file)

    console.print(f'[bold]Configuration:[/bold] {config_file.absolute()}\n')
    console.print('[info]Project[/info]')
    console.print(f'  Name:      {cfg.project_name}')
    console.print(f'  Directory: {cfg.project_path}\n')

    console.print('[info]Models[/info]')
    console.print(
        f'  Flow model:     {cfg.project_settings["models"]["flow_models"][0]}'
    )
    console.print(f'  Reaction model: {cfg.reaction_model_name}\n')

    start, end = cfg.reaction_start_stress_range
    end_str = '∞' if end > 1_000_000 else str(end)
    console.print('[info]Reaction stress periods[/info]')
    console.print(f'  Start: {start}')
    console.print(f'  End:   {end_str}\n')

    console.print('[info]Paths[/info]')
    console.print(f'  MF6:      {cfg.mf6_path}')
    console.print(f'  PhreeqcRM: {cfg.phreeqcrm_path}')
    console.print(f'  rtmf6:    {cfg.rtmf6_path}\n')

    phr = cfg.project_settings['phreeqcrm']
    console.print('[info]PhreeqcRM[/info]')
    console.print(f'  Database: {phr["database"]}')
    console.print(f'  Chemistry: {phr["chemistry_name"]}')


# Subcommand name to function mapping for disambiguation workaround.
# Note: "run" is handled specially in callback() since it needs parameters.
_SUBCOMMANDS = {
    'run': run,
    'info': info,
    'config': config_cmd,
}


def main() -> None:
    """Entry point for the CLI."""
    mp.set_start_method('spawn')
    app()


if __name__ == '__main__':
    main()
