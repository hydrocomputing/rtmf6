"""Adjust file prefixes."""

from pathlib import Path
from shutil import copyfile


def get_model_file_names(file_name):
    """Get file names for models from `mfsin.nam`."""
    model_file_names = {}
    with open(file_name) as fobj:
        in_block = False
        for line in fobj:
            processed_line = line.strip().lower()
            if (
                processed_line.startswith('begin')
                and processed_line.split()[1] == 'models'
            ):
                in_block = True
                continue
            if in_block:
                if processed_line.startswith('end'):
                    break
                else:
                    model_type, file_name, *_ = line.split()
                    model_file_names.setdefault(model_type, []).append(
                        file_name
                    )
    return model_file_names


def prefix_file_paths(
    in_text,
    blocks,
    skip_model_types=None,
    skip_file_names=None,
    prefix='../../../mf6/',
):
    """Prefix path to files."""
    if skip_file_names is None:
        skip_file_names = []
    skip_file_names = set(skip_file_names)
    skipped = {}
    if skip_model_types:
        skip_model_types = [entry.lower() for entry in skip_model_types]
    out = []
    in_block = False
    for line in in_text.splitlines():
        processed_line = line.strip().lower()
        if processed_line.startswith('begin'):
            if processed_line.split()[1] in blocks:
                in_block = True
                out.append(line)
                continue
        if processed_line.startswith('end'):
            if processed_line.split()[1] in blocks:
                in_block = False
        if in_block:
            entry_type, file_name, *_ = line.split()
            if file_name in skip_file_names:
                modified_line = line
            else:
                key = entry_type.lower()
                if skip_model_types and key in skip_model_types:
                    modified_line = line
                    skipped.setdefault(key, []).append(file_name)
                else:
                    modified_line = line.replace(file_name, prefix + file_name)
            out.append(modified_line)
        else:
            out.append(line)
    return skipped, '\n'.join(out)


def prefix_mfsim_name(
    file_name,
    simulate=False,
    backup=False,
    skip_model_types=None,
    skip_file_names=None,
    blocks={'timing', 'models', 'exchanges', 'solutiongroup'},
):
    """Prefix paths in mfsim."""
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text()
    skipped, out_text = prefix_file_paths(
        in_text=in_text,
        skip_model_types=skip_model_types,
        skip_file_names=skip_file_names,
        blocks=blocks,
    )
    if simulate:
        return out_text
    else:
        Path(file_name).write_text(out_text)
        return skipped


def prefix_model_name(
    file_name,
    skip_model_types=None,
    skip_file_names=None,
    simulate=False,
    backup=False,
    blocks={'packages'},
):
    """Prefix path to package files."""
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text()
    skipped, out_text = prefix_file_paths(
        in_text=in_text,
        skip_model_types=skip_model_types,
        skip_file_names=skip_file_names,
        blocks=blocks,
    )
    if simulate:
        return out_text
    else:
        Path(file_name).write_text(out_text)
        return skipped


def prefix_all(
    mfsim, simulate=False, skip_mfsim=None, skip_model_names=None, backup=False
):
    """Prefix all paths in files."""
    if skip_model_names is None:
        skip_model_names = {}
    if skip_mfsim is None:
        skip_mfsim = {}
    mfsim = Path(mfsim)
    needed_names_files = [mfsim.name]
    needed_package_files = {}
    for model_type, names in get_model_file_names(mfsim).items():
        skipped_type = {}
        for name in names:
            skipped = prefix_model_name(
                mfsim.parent / name,
                backup=backup,
                skip=skip_model_names.get(model_type),
                simulate=simulate,
            )
            for key, name_list in skipped.items():
                skipped_type.setdefault(key, []).extend(name_list)
            if simulate:
                print(skipped)
        needed_package_files[model_type] = skipped_type
    needed_names_files = prefix_mfsim_name(
        mfsim, backup=backup, skip=skip_mfsim, simulate=simulate
    )
    return {
        'needed_names_files': needed_names_files,
        'tdis_file_name': needed_names_files.pop('tdis6')[0],
        'needed_package_files': needed_package_files,
    }
