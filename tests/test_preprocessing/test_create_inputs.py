"""Tests for creating the species-specific component models."""

from pathlib import Path
from shutil import copytree, ignore_patterns

import pytest

from rtmf6.config import Config
from rtmf6.preprocessing.create_inputs import make_inputs

TESTS_PATH = Path(__file__).parents[1]

FLAT = {
    'model': TESTS_PATH / 'advect_reactive',
    'chd': 'gwf_advect10.chd',
    'ic': 'gwt_advect10.ic',
    'gwf_nam': 'gwf_advect10.nam',
}
HIERARCHICAL = {
    'model': TESTS_PATH / 'hierarchical-mf6-input' / 'advect_reactive',
    'chd': 'gwf_advect10/gwf_advect10.chd',
    'ic': 'gwt_advect10/gwt_advect10.ic',
    'gwf_nam': 'gwf_advect10/gwf_advect10.nam',
}


def _package_entries(nam_file):
    entries = {}
    in_block = False
    for line in nam_file.read_text(encoding='utf-8').splitlines():
        lower = line.strip().lower()
        if lower.startswith('begin packages'):
            in_block = True
        elif lower.startswith('end packages'):
            in_block = False
        elif in_block and lower:
            package_type, file_name, *_ = line.split()
            entries[package_type.lower()] = file_name
    return entries


@pytest.fixture(params=[FLAT, HIERARCHICAL], ids=['flat', 'hierarchical'])
def project(request, tmp_path):
    """Copy of a test model with freshly created inputs."""
    model = request.param
    copytree(
        model['model'],
        tmp_path,
        dirs_exist_ok=True,
        ignore=ignore_patterns('.internal'),
    )
    config = Config(tmp_path / 'rtmf6.toml')
    make_inputs(config)
    return config, model


def test_species_files_written(project):
    config, model = project
    component = config.internal_paths.component_models_path / 'H'
    assert (component / 'mfsim.nam').is_file()
    for key in ['chd', 'ic', 'gwf_nam']:
        assert (component / model[key]).is_file(), model[key]


def test_species_files_differ_from_template(project):
    config, model = project
    component = config.internal_paths.component_models_path / 'Na'
    for key in ['chd', 'ic']:
        assert (component / model[key]).read_text(encoding='utf-8') != (
            config.mf6_path / model[key]
        ).read_text(encoding='utf-8')


def test_nam_entries(project):
    config, model = project
    component = config.internal_paths.component_models_path / 'H'
    entries = _package_entries(component / model['gwf_nam'])
    assert entries['chd6'] == model['chd']
    for package_type in ['dis6', 'ic6', 'npf6', 'oc6']:
        entry = entries[package_type]
        assert entry.startswith('../../../mf6/')
        # paths are relative to the directory of mfsim.nam
        assert (component / entry).resolve().is_file(), entry
