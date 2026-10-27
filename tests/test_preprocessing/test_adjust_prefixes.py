"""Tests for prefixing file paths in MF6 name files."""

from rtmf6.preprocessing.adjust_prefixes import prefix_file_paths

NAM_FLAT = """\
BEGIN options
  SAVE_FLOWS
END options

BEGIN packages
  DIS6  gwf.dis  dis
  CHD6  gwf.chd  chd-1
END packages"""

NAM_HIERARCHICAL = """\
BEGIN packages
  DIS6  gwf/gwf.dis  dis
  CHD6  gwf/gwf.chd  chd-1
END packages"""


def _package_lines(text):
    return [line.split()[1] for line in text.splitlines()[1:-1]]


def test_flat_skip_by_file_name():
    _, out = prefix_file_paths(
        NAM_FLAT, blocks={'packages'}, skip_file_names=['gwf.chd']
    )
    assert 'SAVE_FLOWS' in out
    assert _package_lines(out.split('\n\n')[1]) == [
        '../../../mf6/gwf.dis',
        'gwf.chd',
    ]


def test_hierarchical_skip_by_relative_path():
    _, out = prefix_file_paths(
        NAM_HIERARCHICAL,
        blocks={'packages'},
        skip_file_names=['gwf/gwf.chd'],
    )
    assert _package_lines(out) == ['../../../mf6/gwf/gwf.dis', 'gwf/gwf.chd']


def test_hierarchical_skip_normalizes_paths():
    nam = NAM_HIERARCHICAL.replace('gwf/gwf.chd', './gwf/gwf.chd')
    _, out = prefix_file_paths(
        nam, blocks={'packages'}, skip_file_names=['gwf/gwf.chd']
    )
    assert _package_lines(out) == ['../../../mf6/gwf/gwf.dis', './gwf/gwf.chd']


def test_hierarchical_same_file_name_other_dir_is_prefixed():
    nam = NAM_HIERARCHICAL.replace('gwf/gwf.dis', 'other/gwf.chd')
    _, out = prefix_file_paths(
        nam, blocks={'packages'}, skip_file_names=['gwf/gwf.chd']
    )
    assert _package_lines(out) == ['../../../mf6/other/gwf.chd', 'gwf/gwf.chd']


def test_absolute_path_is_not_prefixed(tmp_path):
    abs_path = (tmp_path / 'gwf.dis').as_posix()
    nam = NAM_HIERARCHICAL.replace('gwf/gwf.dis', abs_path)
    _, out = prefix_file_paths(nam, blocks={'packages'})
    assert _package_lines(out) == [abs_path, '../../../mf6/gwf/gwf.chd']
