import os
import pathlib
import shutil
import subprocess
import time

import pytest

from gird.gird import RunConfig, SubcommandResult
from gird.gird import run_rule as gird_run_rule
from gird.girdfile import import_girdfile


@pytest.fixture
def run():
    def _run(
        pytest_tmp_path: pathlib.Path,
        *args,
        raise_on_error: bool = True,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Helper function for using subprocess.run in Pytest tmp_path.

        stdout & stderr will be set to subprocess.PIPE.

        Parameters
        ----------
        pytest_tmp_path
            Temporary directory to run a test in. Will be added to PYTHONPATH
            environment variable, and used as cwd in the subprocess.run call.
        args
            Positional arguments for subprocess.run.
        raise_on_error
            If True, raise a RuntimeError if the returncode of the command
            returns non-zero exit code.
        kwargs
            Keyword arguments for subprocess.run.
        """
        # pytest_tmp_path is not the directory where pytest is originally
        # invoked, so it must be added to PYTHONPATH.
        pythonpath = os.environ.get("PYTHONPATH", "")
        if pythonpath:
            pythonpath += os.pathsep
        pythonpath += str(pytest_tmp_path.resolve())
        os.environ["PYTHONPATH"] = pythonpath

        process = subprocess.run(
            *args,
            cwd=pytest_tmp_path,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs,
        )

        if raise_on_error and process.returncode != 0:
            command = " ".join(*args)
            raise RuntimeError(
                f"Command `{command}` returned exit code {process.returncode}.\n"
                f"Stderr:\n{process.stderr}"
                f"Stdout:\n{process.stdout}"
            )

        return process

    return _run


def _init_tmp_path(
    pytest_tmp_path: pathlib.Path,
    test_dir: pathlib.Path,
) -> pathlib.Path:
    """Initialize pytest tmp_path for Gird, i.e., copy girdfile from test_dir
    to pytest_tmp_path.

    Parameters
    ----------
    pytest_tmp_path
        pytest's tmp_path fixture
    test_dir
        Test directory with girdfile.py

    Returns
    -------
    girdfile_path
        Path of a copied girdfile.py to be used by Gird.
    """
    path_girdfile_original = test_dir / "girdfile.py"
    # Use a unique name for the girdfile because the multiprocessing library
    # may get confused on some environments if names must be imported from
    # multiple modules with the same name.
    path_girdfile = pytest_tmp_path / f"girdfile_{test_dir.name}.py"
    shutil.copy(path_girdfile_original, path_girdfile)
    return path_girdfile


@pytest.fixture
def init_tmp_path():
    return _init_tmp_path


@pytest.fixture
def run_rule(run):
    def _run_rule(
        pytest_tmp_path: pathlib.Path,
        test_dir: pathlib.Path,
        target: str,
        dry_run: bool = False,
        question: bool = False,
        output_sync: bool = False,
    ) -> SubcommandResult:
        """Import Rules from a girdfile and run one of them.

        Parameters
        ----------
        pytest_tmp_path
            Temporary directory to run this test in.
        test_dir
            Original test directory with girdfile.py. If the directory also
            contains files named Makefile1 & Makefile2, those will be compared
            to the Makefiles produced by Gird.
        target
            The id of the target of the rule to be run, i.e., as it would be
            given in the CLI.
        dry_run
            See CLI argument '--dry-run'.
        question
            See CLI argument '--question'.
        """
        girdfile = _init_tmp_path(
            pytest_tmp_path=pytest_tmp_path,
            test_dir=test_dir,
        )

        os.chdir(pytest_tmp_path)

        rules = import_girdfile(girdfile)

        for rule in rules:
            if target == rule.target.id:
                target = rule.target
                break
        else:
            raise ValueError(f"Target '{target}' not defined in '{girdfile}'.")

        run_config = RunConfig(
            target=target,
            verbose=False,
            question=question,
            dry_run=dry_run,
            output_sync=output_sync,
        )

        result = gird_run_rule(
            rules,
            run_config,
        )

        # Wait to make sure targets created by different calls get different
        # timestamps.
        time.sleep(0.001)

        return result

    return _run_rule
