"""Adjust file prefixes."""

from pathlib import Path
from shutil import copyfile


def get_model_file_names(file_name):
    model_file_names = {}
    with open(file_name) as fobj:
        in_block = False
        for line in fobj:
            processed_line = line.strip().lower()
            if processed_line.startswith('begin') and processed_line.split()[1] == 'models':
                in_block = True
                continue
            if in_block:
                if processed_line.startswith('end'):
                    break
                else:
                    model_type, file_name, *_ = line.split()
                    model_file_names.setdefault(model_type, []).append(file_name)
    return model_file_names

def prefix_file_paths(in_text, blocks, skip=None, prefix='../../base_model/common_inputs/'):
    skipped = []
    if skip:
        skip = [entry.lower() for entry in skip]
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
            if skip and entry_type.lower() in skip:
                modified_line = line
                skipped.append(file_name)
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
    blocks={'timing', 'models', 'exchanges', 'solutiongroup'}):
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text()
    _, out_text = prefix_file_paths(in_text=in_text, blocks=blocks)
    if simulate:
        return out_text
    else:
        Path(file_name).write_text(out_text)

def prefix_model_name(
    file_name,
    skip,
    simulate=False,
    backup=False,
    blocks={'packages'}):
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text()
    skipped, out_text = prefix_file_paths(in_text=in_text, skip=skip, blocks=blocks)
    if simulate:
        return out_text
    else:
        Path(file_name).write_text(out_text)
        return skipped

def prefix_all(mfsim, simulate=False, skip=None):
    if skip is None:
        skip = {}
    mfsim = Path(mfsim)
    needed_files = [mfsim.name]
    for model_type, names in get_model_file_names(mfsim).items():
        for name in names:
            skipped = prefix_model_name(
                mfsim.parent / name,
                backup=True,
                skip=skip[model_type],
                simulate=simulate)
            needed_files.append(name)
            needed_files.extend(skipped)
            if simulate:
                print(skipped)
    prefix_mfsim_name(mfsim, backup=True, simulate=simulate)
    return needed_files