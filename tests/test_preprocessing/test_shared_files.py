"""Tests for shared copies of files that reference other files."""

import pytest

from rtmf6.preprocessing.adjust_prefixes import SharedFiles

NPF = """\
BEGIN options
  TS6 FILEIN gwf/npf.ts
END options

BEGIN griddata
  icelltype
    constant 1
  k
    OPEN/CLOSE gwf/npf/k.dat FACTOR 1.0
# open/close gwf/npf/comment.dat
  k33
    open/close 'gwf/npf/k 33.dat' (BINARY)
END griddata
"""

TDIS = """\
BEGIN options
  ATS6 FILEIN ats.ats
END options
"""

ATS = """\
BEGIN perioddata
  open/close ats/perioddata.dat
END perioddata
"""

IMS = """\
BEGIN options
  PRINT_OPTION summary
END options
"""


@pytest.fixture
def shared_files(tmp_path):
    """Shared files for an MF6 directory with file references."""
    mf6_path = tmp_path / 'mf6'
    for name, text in {
        'gwf/npf.npf': NPF,
        'gwf/npf.ts': 'BEGIN attributes\nEND attributes\n',
        'tdis.tdis': TDIS,
        'ats.ats': ATS,
        'ims.ims': IMS,
    }.items():
        path = mf6_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    shared_path = tmp_path / '.internal' / 'shared'
    return SharedFiles(mf6_path=mf6_path, shared_path=shared_path)


def test_file_without_references_is_prefixed(shared_files):
    assert shared_files.reference('ims.ims') == '../../../mf6/ims.ims'
    assert not (shared_files.shared_path / 'ims.ims').exists()


def test_file_with_references_is_shared(shared_files):
    assert shared_files.reference('gwf/npf.npf') == '../../shared/gwf/npf.npf'
    text = (shared_files.shared_path / 'gwf/npf.npf').read_text(
        encoding='utf-8'
    )
    assert 'TS6 FILEIN ../../../mf6/gwf/npf.ts' in text
    assert 'OPEN/CLOSE ../../../mf6/gwf/npf/k.dat FACTOR 1.0' in text
    assert "open/close '../../../mf6/gwf/npf/k 33.dat' (BINARY)" in text
    # comments are not modified
    assert '# open/close gwf/npf/comment.dat' in text


def test_filein_with_references_is_shared_recursively(shared_files):
    assert shared_files.reference('tdis.tdis') == '../../shared/tdis.tdis'
    shared_path = shared_files.shared_path
    tdis = (shared_path / 'tdis.tdis').read_text(encoding='utf-8')
    assert 'ATS6 FILEIN ../../shared/ats.ats' in tdis
    ats = (shared_path / 'ats.ats').read_text(encoding='utf-8')
    assert 'open/close ../../../mf6/ats/perioddata.dat' in ats


def test_absolute_paths_unchanged(shared_files, tmp_path):
    abs_path = (tmp_path / 'k.dat').as_posix()
    assert shared_files.reference(abs_path) == abs_path
    npf = shared_files.mf6_path / 'gwf/npf.npf'
    # only absolute references, works from all directories
    npf.write_text(f'  k\n    open/close {abs_path}\n', encoding='utf-8')
    assert shared_files.reference('gwf/npf.npf') == '../../../mf6/gwf/npf.npf'
    sto = shared_files.mf6_path / 'gwf/sto.sto'
    sto.write_text(
        f'  ss\n    open/close {abs_path}\n  sy\n    open/close gwf/sy.dat\n',
        encoding='utf-8',
    )
    assert shared_files.reference('gwf/sto.sto') == '../../shared/gwf/sto.sto'
    text = (shared_files.shared_path / 'gwf/sto.sto').read_text(
        encoding='utf-8'
    )
    assert f'open/close {abs_path}' in text
    assert 'open/close ../../../mf6/gwf/sy.dat' in text


def test_out_of_tree_file_stays_inside_shared_path(shared_files):
    mf6_path = shared_files.mf6_path
    outside = mf6_path.parent / 'scenario' / 'npf.npf'
    outside.parent.mkdir()
    outside.write_text('  k\n    open/close ../scenario/k.dat\n')
    reference = shared_files.reference('../scenario/npf.npf')
    assert reference == '../../shared/_up_/scenario/npf.npf'
    text = (shared_files.shared_path / '_up_/scenario/npf.npf').read_text(
        encoding='utf-8'
    )
    assert 'open/close ../../../mf6/../scenario/k.dat' in text


DIS = """\
BEGIN options
  LENGTH_UNITS meters
END options

BEGIN griddata
  top
    open/close gwf/dis/top.dat
END griddata
"""


def test_nogrb_copy_of_shared_file(shared_files):
    (shared_files.mf6_path / 'gwf/dis.dis').write_text(DIS, encoding='utf-8')
    reference = shared_files.reference('gwf/dis.dis', nogrb=True)
    assert reference == '../../shared/_nogrb/gwf/dis.dis'
    text = (shared_files.shared_path / '_nogrb/gwf/dis.dis').read_text(
        encoding='utf-8'
    )
    assert 'BEGIN options\n  NOGRB\n  LENGTH_UNITS meters' in text
    assert 'open/close ../../../mf6/gwf/dis/top.dat' in text
    # the copy for writing the binary grid file is not modified
    assert shared_files.reference('gwf/dis.dis') == '../../shared/gwf/dis.dis'
    text = (shared_files.shared_path / 'gwf/dis.dis').read_text(
        encoding='utf-8'
    )
    assert 'NOGRB' not in text


def test_nogrb_copy_without_options_block(shared_files):
    dis = 'BEGIN griddata\n  top\n    constant 1.0\nEND griddata\n'
    (shared_files.mf6_path / 'dis.dis').write_text(dis, encoding='utf-8')
    reference = shared_files.reference('dis.dis', nogrb=True)
    assert reference == '../../shared/_nogrb/dis.dis'
    text = (shared_files.shared_path / '_nogrb/dis.dis').read_text(
        encoding='utf-8'
    )
    assert text == 'BEGIN options\n  NOGRB\nEND options\n\n' + dis
