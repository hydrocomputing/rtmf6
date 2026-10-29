"""Adjust file prefixes."""

from pathlib import Path, PurePosixPath
import re
from shutil import copyfile

FILE_REFERENCE = re.compile(
    r"""(?P<keyword>\b(?:open/close|filein))(?P<space>\s+)"""
    r"""(?:(?P<quote>['"])(?P<quoted>.+?)(?P=quote)|(?P<plain>[^\s'"]+))""",
    flags=re.IGNORECASE,
)
OPTIONS_BEGIN = re.compile(
    r'^[ \t]*begin[ \t]+options\b.*(?:\n|$)', flags=re.IGNORECASE | re.MULTILINE
)
NOGRB = re.compile(r'^\s*nogrb\b', flags=re.IGNORECASE | re.MULTILINE)


def normalize_file_name(file_name):
    """Normalize a file name relative to the directory of `mfsim.nam`.

    MF6 resolves all paths in all name files relative to the simulation
    directory. Normalizing allows comparing paths such as `./gwf/gwf.chd`
    and `gwf\\gwf.chd` with `gwf/gwf.chd`.
    """
    return str(PurePosixPath(str(file_name).replace('\\', '/')))


class SharedFiles:
    """Shared copies of files that reference other files.

    MF6 resolves the paths after `OPEN/CLOSE` and `FILEIN` relative to the
    simulation directory, i.e. the directory of the component model.
    Files that contain such paths are copied once to `shared_path` with
    adjusted paths. All component models use these copies.
    `mf6_prefix` and `shared_prefix` are relative to a component model.
    """

    def __init__(
        self,
        mf6_path,
        shared_path,
        mf6_prefix='../../../mf6/',
        shared_prefix='../../shared/',
    ):
        self.mf6_path = mf6_path
        self.shared_path = shared_path
        self.mf6_prefix = mf6_prefix
        self.shared_prefix = shared_prefix
        # normalized file name -> name in `shared_path` or `None`
        self._shared_names = {}

    def reference(self, file_name, nogrb=False):
        """Reference to `file_name` for use in a component model.

        Use `nogrb=True` for a copy of a DIS file with the option `NOGRB`.
        """
        if Path(file_name).is_absolute():
            return file_name
        shared_name = self._make_shared_copy(file_name)
        if nogrb:
            nogrb_name = self._make_nogrb_copy(file_name, shared_name)
            if nogrb_name is not None:
                return self.shared_prefix + nogrb_name
        if shared_name is None:
            return self.mf6_prefix + file_name
        return self.shared_prefix + shared_name

    def _make_nogrb_copy(self, file_name, shared_name):
        """Copy a DIS file and add option `NOGRB`.

        All component models write the same binary grid file.
        Writing it once is sufficient.
        Return `None` if the file already has the option `NOGRB`.
        """
        key = normalize_file_name(file_name)
        if shared_name is None:
            src = self.mf6_path / key
        else:
            src = self.shared_path / shared_name
        text = src.read_text(encoding='utf-8', errors='surrogateescape')
        if NOGRB.search(text):
            return None
        nogrb_name = '_nogrb/' + key.replace('..', '_up_')
        target = self.shared_path / nogrb_name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                add_nogrb(text), encoding='utf-8', errors='surrogateescape'
            )
        return nogrb_name

    def _make_shared_copy(self, file_name):
        """Copy file with adjusted references if it references files."""
        key = normalize_file_name(file_name)
        if key not in self._shared_names:
            # set before recursion to prevent cycles
            self._shared_names[key] = None
            path = self.mf6_path / key
            if path.is_file():
                text = path.read_text(
                    encoding='utf-8', errors='surrogateescape'
                )
                new_text = self._adjust_references(text)
                if new_text != text:
                    # keep out-of-tree files such as `../x.npf` inside
                    shared_name = key.replace('..', '_up_')
                    target = self.shared_path / shared_name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(
                        new_text, encoding='utf-8', errors='surrogateescape'
                    )
                    self._shared_names[key] = shared_name
        return self._shared_names[key]

    def _adjust_references(self, text):
        lines = []
        for line in text.splitlines(keepends=True):
            if line.strip()[:1] not in {'#', '!'}:
                line = FILE_REFERENCE.sub(self._replace_reference, line)
            lines.append(line)
        return ''.join(lines)

    def _replace_reference(self, match):
        keyword = match['keyword']
        quote = match['quote'] or ''
        file_name = match['quoted'] if quote else match['plain']
        if keyword.lower() == 'filein':
            # files read with `FILEIN` can reference files too
            new_name = self.reference(file_name)
        elif Path(file_name).is_absolute():
            new_name = file_name
        else:
            new_name = self.mf6_prefix + file_name
        return f'{keyword}{match["space"]}{quote}{new_name}{quote}'


def add_nogrb(text):
    """Add option `NOGRB` to the text of DIS file."""
    if NOGRB.search(text):
        return text
    match = OPTIONS_BEGIN.search(text)
    if match is None:
        return 'BEGIN options\n  NOGRB\nEND options\n\n' + text
    begin = match.group()
    if not begin.endswith('\n'):
        begin += '\n'
    return text[: match.start()] + begin + '  NOGRB\n' + text[match.end():]


def get_model_file_names(file_name):
    """Get file names for models from `mfsin.nam`."""
    model_file_names = {}
    with open(file_name, encoding='utf-8') as fobj:
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
    make_reference=None,
):
    """Prefix path to files.

    `make_reference` is a callable that takes a file name and the entry
    type, e.g. `dis6`, and returns the new reference for this file name.
    It replaces `prefix` if given.
    """
    # pylint: disable=too-many-branches, too-many-locals
    if skip_file_names is None:
        skip_file_names = []
    skip_file_names = {normalize_file_name(name) for name in skip_file_names}
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
        if in_block and processed_line and processed_line[0] not in '#!':
            entry_type, file_name, *_ = line.split()
            if (
                normalize_file_name(file_name) in skip_file_names
                # absolute paths work from all directories
                or Path(file_name).is_absolute()
            ):
                modified_line = line
            else:
                key = entry_type.lower()
                if skip_model_types and key in skip_model_types:
                    modified_line = line
                    skipped.setdefault(key, []).append(file_name)
                else:
                    if make_reference is None:
                        new_name = prefix + file_name
                    else:
                        new_name = make_reference(file_name, entry_type)
                    modified_line = line.replace(file_name, new_name, 1)
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
    blocks=frozenset({'timing', 'models', 'exchanges', 'solutiongroup'}),
    make_reference=None,
):
    """Prefix paths in mfsim."""
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text(encoding='utf-8')
    skipped, out_text = prefix_file_paths(
        in_text=in_text,
        skip_model_types=skip_model_types,
        skip_file_names=skip_file_names,
        blocks=blocks,
        make_reference=make_reference,
    )
    if simulate:
        return out_text
    Path(file_name).write_text(out_text, encoding='utf-8')
    return skipped


def prefix_model_name(
    file_name,
    skip_model_types=None,
    skip_file_names=None,
    simulate=False,
    backup=False,
    blocks=frozenset({'packages'}),
    make_reference=None,
):
    """Prefix path to package files."""
    if backup:
        copyfile(file_name, file_name.parent / (file_name.name + '.bak'))
    in_text = Path(file_name).read_text(encoding='utf-8')
    skipped, out_text = prefix_file_paths(
        in_text=in_text,
        skip_model_types=skip_model_types,
        skip_file_names=skip_file_names,
        blocks=blocks,
        make_reference=make_reference,
    )
    if simulate:
        return out_text
    Path(file_name).write_text(out_text, encoding='utf-8')
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
                skip_file_names=skip_model_names.get(model_type),
                simulate=simulate,
            )
            for key, name_list in skipped.items():
                skipped_type.setdefault(key, []).extend(name_list)
            if simulate:
                print(skipped)
        needed_package_files[model_type] = skipped_type
    needed_names_files = prefix_mfsim_name(
        mfsim, backup=backup, skip_file_names=skip_mfsim, simulate=simulate
    )
    return {
        'needed_names_files': needed_names_files,
        'tdis_file_name': needed_names_files.pop('tdis6')[0],
        'needed_package_files': needed_package_files,
    }
