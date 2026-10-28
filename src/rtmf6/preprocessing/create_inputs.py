"""Create the input files.

Read selected model input files with flopy, modify some values such
as initial concentrations and concentration values of boundary,
and write files back.
"""

from shutil import copyfile, rmtree

from rtmf6.preprocessing.adjust_prefixes import (
    SharedFiles,
    get_model_file_names,
    prefix_mfsim_name,
    prefix_model_name,
)
from rtmf6.preprocessing.flopy_setup import FlopyWorker
from rtmf6.preprocessing.phreeqc_setup import PhreeqcCellMappings, YAMLCreator


def make_inputs(config):
    """Create rtmf6 input files."""
    worker = FlopyWorker(config)
    worker.update_all()
    _make_nam_files(config, files_names_to_skip=worker.modified_rel_paths)
    make_phreeqcrm_yaml(config, flopy_worker=worker)


# discretization packages write a binary grid file
DIS_TYPES = frozenset({'dis6', 'disv6', 'disu6'})


def _make_nam_files(config, files_names_to_skip):
    """Create nam files for all component models.

    All component models would write the same binary grid file.
    Only the first one writes it, all others use DIS files with `NOGRB`.
    """
    shared_path = config.internal_paths.shared_path
    if shared_path.exists():
        rmtree(shared_path)
    shared_files = SharedFiles(
        mf6_path=config.mf6_path, shared_path=shared_path
    )
    nam_paths = {}
    for nogrb, target_path in [
        (False, config.internal_paths.work_path_nam),
        (True, config.internal_paths.work_path_nam_nogrb),
    ]:
        _make_nam_file_set(
            config,
            files_names_to_skip,
            target_path,
            make_reference=_make_reference_function(shared_files, nogrb),
        )
        nam_paths[nogrb] = target_path
    components = sorted(
        path
        for path in config.internal_paths.component_models_path.iterdir()
        if path.is_dir()
    )
    for index, component in enumerate(components):
        _copy_nam_files(src_path=nam_paths[index > 0], dst_path=component)


def _make_reference_function(shared_files, nogrb):
    """Make function that returns the reference to a file."""

    def make_reference(file_name, entry_type):
        return shared_files.reference(
            file_name, nogrb=nogrb and entry_type.lower() in DIS_TYPES
        )

    return make_reference


def _make_nam_file_set(
    config, files_names_to_skip, target_path, make_reference
):
    """Create nam files and fix file path prefixes."""
    if target_path.exists():
        rmtree(target_path)
    target_path.mkdir(parents=True)
    mfsim_in = config.mf6_path / 'mfsim.nam'
    mfsim_out = target_path / 'mfsim.nam'
    copyfile(mfsim_in, mfsim_out)
    for file_names in get_model_file_names(mfsim_out).values():
        for file_name in file_names:
            nam_file = target_path / file_name
            nam_file.parent.mkdir(parents=True, exist_ok=True)
            copyfile(config.mf6_path / file_name, nam_file)
            prefix_model_name(
                nam_file,
                skip_file_names=files_names_to_skip,
                make_reference=make_reference,
            )
    prefix_mfsim_name(
        mfsim_out,
        blocks={'timing', 'exchanges', 'solutiongroup'},
        make_reference=make_reference,
    )


def _copy_nam_files(src_path, dst_path):
    """Copy name files to a component dir, keeping sub directories."""
    for file in src_path.rglob('*'):
        if file.is_file():
            dst = dst_path / file.relative_to(src_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            copyfile(file, dst)


def make_phreeqcrm_yaml(config, flopy_worker):
    """Create PhreeqcRM YAML file.."""
    phr_mappings = PhreeqcCellMappings(config, flopy_worker=flopy_worker)
    cell_mappings = phr_mappings.make_mappings()
    yaml_creator = YAMLCreator(config, cell_mappings, nxyz=flopy_worker.nxyz)
    yaml_creator.make_phreeqcrm_yaml()
