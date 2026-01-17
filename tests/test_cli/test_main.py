"""Tests for the rtmf6 CLI."""

import pytest
from typer.testing import CliRunner

from rtmf6.main import app, __version__


runner = CliRunner()


@pytest.fixture
def mock_model_execution(mocker):
    """Mock the model execution functions to avoid running actual numerical models."""
    mocker.patch("rtmf6.main.make_inputs")
    mocker.patch("rtmf6.main.run_rtmf6")


class TestVersion:
    """Tests for version display."""

    def test_version_flag(self):
        """Test --version flag shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "rtmf6 version" in result.output

    def test_version_flag_short(self):
        """Test -V flag shows version."""
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestHelp:
    """Tests for help display."""

    def test_help_flag(self):
        """Test --help flag shows help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "rtmf6" in result.output
        assert "run" in result.output
        assert "info" in result.output
        assert "config" in result.output

    def test_help_flag_short(self):
        """Test -h flag shows help."""
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "rtmf6" in result.output

    def test_run_help(self):
        """Test run --help shows run command help."""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Run the rtmf6 model" in result.output
        assert "--no-reactions" in result.output
        assert "--preprocess-only" in result.output
        assert "--run-only" in result.output

    def test_info_help(self):
        """Test info --help shows info command help."""
        result = runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_config_help(self):
        """Test config --help shows config command help."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "configuration" in result.output.lower()


class TestInfo:
    """Tests for info subcommand."""

    def test_info_shows_version(self):
        """Test info command shows version."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "rtmf6" in result.output


class TestConfig:
    """Tests for config subcommand."""

    def test_config_shows_project_info(self, fixtures_path, monkeypatch):
        """Test config command shows project information."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configuration:" in result.output
        assert "Project" in result.output
        assert "cat_ex_1d" in result.output

    def test_config_shows_models(self, fixtures_path, monkeypatch):
        """Test config command shows model information."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Models" in result.output
        assert "gwf_cat_ex_1d" in result.output
        assert "gwt_cat_ex_1d" in result.output

    def test_config_shows_paths(self, fixtures_path, monkeypatch):
        """Test config command shows paths."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Paths" in result.output
        assert "MF6" in result.output
        assert "PhreeqcRM" in result.output

    def test_config_shows_phreeqcrm(self, fixtures_path, monkeypatch):
        """Test config command shows PhreeqcRM settings."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "PhreeqcRM" in result.output
        assert "Database" in result.output
        assert "phreeqc.dat" in result.output

    def test_config_no_file_in_cwd(self, tmp_path, monkeypatch):
        """Test config without config file in current directory shows error."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["config"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()


class TestRun:
    """Tests for run subcommand."""

    def test_run_success(self, fixtures_path, monkeypatch, mock_model_execution):
        """Test successful run command."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 0
        assert "rtmf6" in result.output
        assert "run complete" in result.output.lower()


class TestRunWithOptions:
    """Tests for run with options.

    Note: Due to the CLI structure with callback + subcommands, options must be
    placed BEFORE the subcommand name, e.g., `rtmf6 --preprocess-only run`
    rather than `rtmf6 run --preprocess-only`.
    """

    def test_run_preprocess_only(self, fixtures_path, monkeypatch, mock_model_execution):
        """Test run with --preprocess-only flag (option before subcommand)."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["--preprocess-only", "run"])
        assert result.exit_code == 0
        assert "Preprocessing only" in result.output

    def test_run_preprocess_only_short(self, fixtures_path, monkeypatch, mock_model_execution):
        """Test run with -p flag (option before subcommand)."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["-p", "run"])
        assert result.exit_code == 0
        assert "Preprocessing only" in result.output

    def test_conflicting_options(self, fixtures_path, monkeypatch, mock_model_execution):
        """Test run with both --preprocess-only and --run-only shows error."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, ["--preprocess-only", "--run-only", "run"])
        assert result.exit_code != 0
        assert "cannot both be specified" in result.output.lower()


class TestRunErrors:
    """Tests for run command error handling."""

    def test_run_no_config_in_cwd(self, tmp_path, monkeypatch):
        """Test run without config file in current directory shows error."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["run"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()


class TestDefaultCommand:
    """Tests for default command behavior (running without subcommand)."""

    def test_no_args_no_config(self, tmp_path, monkeypatch):
        """Test running without arguments and no config file shows error."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, [])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_nonexistent_file_as_arg(self):
        """Test running with non-existent file as argument shows error."""
        result = runner.invoke(app, ["nonexistent.toml"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_with_explicit_config_file(self, sample_config, mock_model_execution):
        """Test running with explicit config file path (without subcommand)."""
        result = runner.invoke(app, [str(sample_config)])
        assert result.exit_code == 0
        assert "rtmf6" in result.output
        assert "run complete" in result.output.lower()

    def test_default_in_cwd(self, fixtures_path, monkeypatch, mock_model_execution):
        """Test running without arguments finds rtmf6.toml in current directory."""
        monkeypatch.chdir(fixtures_path)
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "rtmf6" in result.output
        assert "run complete" in result.output.lower()
