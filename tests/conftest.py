import subprocess
import sys
from pathlib import Path

import pytest

repo_path = Path('tests', 'testdata').__str__()
repo1 = Path(repo_path, 'daffy')
repo2 = Path(repo_path, 'porky')
okay = repo1.exists() and repo2.exists()

git_cmd = [
    sys.executable,
    '-m',
    'git_dummy',
    '--allow-nested',
    '--constant-sha',
    '--commits=10',
    '--branches=5',
    '--diverge-at=2',
    '--git-dir',
    repo_path,
]


def pytest_configure(config):
    """Create git repo test data"""
    # can use `config` to use command line options
    print(f'Test repos are okay: {okay}')
    if not okay:
        print(f'Creating dummy git repos in {repo_path}')
        for repo in ('daffy', 'porky'):
            git_cmd.extend(['--name', repo])
            print(f'Running full cmd: {git_cmd}')
            out = subprocess.check_output(git_cmd, universal_newlines=True)
            assert 'Generating dummy Git repo' in out
            # print(f'Out: {out}')
            # print(sorted(Path('tests/testdata').glob('*')))


@pytest.fixture(scope="module")
def script_loc(request):
    """Return the directory of the currently running test script"""

    return request.path.parent


@pytest.fixture(scope='session')
def tmpdir_session(request, tmp_path_factory):
    """A tmpdir fixture for the session scope. Persists throughout the pytest session."""

    return tmp_path_factory.mktemp(tmp_path_factory.getbasetemp().name)
