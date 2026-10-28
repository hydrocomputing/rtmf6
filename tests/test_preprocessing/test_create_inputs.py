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
# MF6 input files use `open/close` to read data from other files
OPEN_CLOSE = {
    'model': TESTS_PATH / 'hierarchical-mf6-input' / 'vmp_5',
    'chd': 'VMP_5_gwf/chd.chd',
    'ic': 'VMP_5_gwt/ic.ic',
    'gwf_nam': 'VMP_5_gwf/VMP_5_gwf.nam',
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


@pytest.fixture(
    scope='module',
    params=[FLAT, HIERARCHICAL, OPEN_CLOSE],
    ids=['flat', 'hierarchical', 'open_close'],
)
def project(request, tmp_path_factory):
    """Copy of a test model with freshly created inputs."""
    model = request.param
    project_path = tmp_path_factory.mktemp('project')
    copytree(
        model['model'],
        project_path,
        dirs_exist_ok=True,
        ignore=ignore_patterns('.internal'),
    )
    config = Config(project_path / 'rtmf6.toml')
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


def test_species_files_self_contained(project):
    config, model = project
    component = config.internal_paths.component_models_path / 'Na'
    for key in ['chd', 'ic']:
        text = (component / model[key]).read_text(encoding='utf-8')
        assert 'open/close' not in text.lower(), model[key]


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


def _move_to_absolute_path(project_path, rel_path, target_path):
    """Move a package file out of the project and reference it absolutely."""
    src = project_path / 'mf6' / rel_path
    dst = target_path / src.name
    src.rename(dst)
    nam_file = project_path / 'mf6' / HIERARCHICAL['gwf_nam']
    nam_file.write_text(
        nam_file.read_text(encoding='utf-8').replace(rel_path, str(dst)),
        encoding='utf-8',
    )
    return dst


@pytest.fixture
def hierarchical_copy(tmp_path):
    """Copy of the hierarchical test model without generated inputs."""
    project_path = tmp_path / 'project'
    copytree(
        HIERARCHICAL['model'],
        project_path,
        ignore=ignore_patterns('.internal'),
    )
    shared_path = tmp_path / 'shared'
    shared_path.mkdir()
    return project_path, shared_path


def test_absolute_path_not_loaded_by_flopy(hierarchical_copy):
    project_path, shared_path = hierarchical_copy
    npf = _move_to_absolute_path(
        project_path, 'gwf_advect10/gwf_advect10.npf', shared_path
    )
    config = Config(project_path / 'rtmf6.toml')
    make_inputs(config)
    component = config.internal_paths.component_models_path / 'H'
    entries = _package_entries(component / HIERARCHICAL['gwf_nam'])
    assert entries['npf6'] == str(npf)


def test_absolute_path_loaded_by_flopy_raises(hierarchical_copy):
    project_path, shared_path = hierarchical_copy
    dis = _move_to_absolute_path(
        project_path, 'gwf_advect10/gwf_advect10.dis', shared_path
    )
    original = dis.read_bytes()
    config = Config(project_path / 'rtmf6.toml')
    with pytest.raises(ValueError, match='absolute path'):
        make_inputs(config)
    # flopy must not overwrite the original file
    assert dis.read_bytes() == original
