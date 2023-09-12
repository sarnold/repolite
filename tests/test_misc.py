import os
from pathlib import Path

import pytest
from munch import Munch

from repolite import *
from repolite.repolite import *


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
    assert 'unknown config file extension' in str(excinfo.value)


def test_parse_config():
    popts, _ = load_config()
    flag_list, repo_list = parse_config(popts)
    assert 'ext' in flag_list
    assert isinstance(repo_list[0], Munch)
    # print(repo_list)
