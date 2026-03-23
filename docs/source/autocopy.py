"""Copy file files to doc tree.

Sphinx can only access files in its root and below.
Copy files over automatically.
"""

from pathlib import Path
from shutil import copyfile


def autocopy(start_path, config_file_name='autocopy.config', target_dir_name='.autocopy'):
    """Copy file files to doc tree.

    All files in listed in a file named `config_file_name` will be
    copied to a directory `target_dir_name` in the same directory.
    """

    for config_file in Path(start_path).rglob(config_file_name):
        config_dir = config_file.parent
        autocopy_dir = config_dir / target_dir_name
        autocopy_dir.mkdir(exist_ok=True)
        sources = (entry for line in config_file.read_text().splitlines() if (entry := line.strip()))
        for source in sources:
            src = (config_dir / source).resolve()
            dst = autocopy_dir / src.name
            copyfile(src, dst)
