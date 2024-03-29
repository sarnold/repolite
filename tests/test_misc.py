import logging
import os
from pathlib import Path

import pytest
from munch import Munch

from repolite import *
from repolite.repolite import *

LOGGER = logging.getLogger(__name__)


def test_git_check():
    git, lfs = check_for_git()
    assert 'git' in git
    assert 'lfs' in lfs or not lfs


def test_url_check():
    url1 = 'https://github.com/sarnold/pyserv.git'
    url2 = 'D:\\a\\repolite\\repolite\\tests\\testdata\\daffy'
    url3 = '/home/user/src/repolite/tests/testdata/porky'
    out2 = 'D:/a/repolite/repolite/tests/testdata/daffy'

    url = check_repo_url(url1)
    assert url == url1
    url = check_repo_url(url2)
    assert url == out2
    url = check_repo_url(url3)
    assert url == url3


def test_resolve_top_dir(tmp_path):
    d = tmp_path / "proj"
    d.mkdir()
    p = d / "proj-test.txt"
    upath = str(d)
    wpath, upath = resolve_top_dir(upath)
    assert upath.exists()


def test_load_config():
    popts, pfile = load_config()

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'repos')
    assert pfile.stem == '.repolite' or 'example'


def test_load_config_env(monkeypatch):
    """monkeypatch env test"""
    monkeypatch.setenv("REPO_CFG", "testme.yml")
    _, pfile = load_config()
    assert isinstance(pfile, Path)


def test_load_config_bogus(monkeypatch):
    """monkeypatch env test"""
    monkeypatch.setenv("REPO_CFG", "testme.txt")
    with pytest.raises(FileTypeError) as excinfo:
        _, pfile = load_config()
    assert 'unknown file extension' in str(excinfo.value)
    assert 'testme.txt' in str(excinfo.value)


def test_parse_config():
    popts, _ = load_config()
    flag_list, repo_list = parse_config(popts)
    assert 'ext' in flag_list
    assert isinstance(repo_list[0], Munch)
    # print(repo_list)
