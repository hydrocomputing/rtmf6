"""Create the input files.

Read selected model input files with flopy, modify some values such
as initial concentrations and concentration values of boundary,
and write files back.
"""

from shutil import copyfile

from rtmf6.preprocessing.adjust_prefixes import get_model_file_names, prefix_mfsim_name, prefix_model_name
from rtmf6.preprocessing.flopy_setup import FlopyWorker
from rtmf6.preprocessing.phreeqc_setup import PhreeqcCellMappings, YAMLCreator


def make_inputs(config):
    """Create rtmf6 input files."""
    worker = FlopyWorker(config)
    worker.update_all()
    file_names = [entry.name for entry in worker.modified_input_files]
    _make_nam_files(config, files_names_to_skip=file_names)
    make_phreeqcrm_yaml(config, flopy_worker=worker)


def _make_nam_files(config, files_names_to_skip):
    """Create nam file and fix file path prefixes."""
    target_path = config.internal_paths.work_path_nam
    mfsim_in = config.mf6_path / 'mfsim.nam'
    mfsim_out = target_path / 'mfsim.nam'
    copyfile(mfsim_in, mfsim_out)
    for file_names in get_model_file_names(mfsim_out).values():
        for file_name in file_names:
            nam_file = target_path / file_name
            copyfile(config.mf6_path / file_name, nam_file)
            prefix_model_name(nam_file, skip_file_names=files_names_to_skip)
    prefix_mfsim_name(mfsim_out, blocks={'timing',  'exchanges', 'solutiongroup'})
    _copy_nam_files(config)


def _copy_nam_files(config):
    """Copy name files tu compnent dirs."""
    src_path = config.internal_paths.work_path_nam
    dst_parent_path = config.internal_paths.component_models_path
    for dst_path in dst_parent_path.iterdir():
        if dst_path.is_dir():
            for file in src_path.iterdir():
                copyfile(file, dst_path / file.name)


def make_phreeqcrm_yaml(config, flopy_worker):
    phr_mappings = PhreeqcCellMappings(config, flopy_worker=flopy_worker)
    cell_mappings = phr_mappings.make_mappings()
    yaml_creator = YAMLCreator(config, cell_mappings, nxyz=flopy_worker.nxyz)
    yaml_creator.make_phreeqcrm_yaml()
