import os
import pathlib
import platform
import shutil
import subprocess
from time import sleep

import pytest


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


@pytest.fixture
def run_rule(run):
    def _run_rule(
        pytest_tmp_path: pathlib.Path,
        test_dir: pathlib.Path,
        rule: str,
    ):
        """Run a rule with Gird.

        Parameters
        ----------
        pytest_tmp_path
            Temporary directory to run this test in.
        test_dir
            Original test directory with girdfile.py. If the directory also
            contains files named Makefile1 & Makefile2, those will be compared
            to the Makefiles produced by Gird.
        rule
            The rule to be run.
        """
        # Copy girdfile.py to pytest_tmp_path.
        path_girdfile_original = test_dir / "girdfile.py"
        path_girdfile = pytest_tmp_path / "girdfile.py"
        shutil.copy(path_girdfile_original, path_girdfile)

        gird_path = pytest_tmp_path / ".gird"
        gird_path_tmp = gird_path / "tmp"

        run(
            pytest_tmp_path,
            ["gird", rule],
        )

        # Assert Makefile contents if there are such files in test_dir.
        for makefile_name in ("Makefile1", "Makefile2"):
            path_makefile_target = test_dir / makefile_name
            path_makefile_result = gird_path_tmp / makefile_name
            if path_makefile_target.exists():
                assert (
                    path_makefile_result.read_text() == path_makefile_target.read_text()
                )

        # Work around timestamp truncation on some Make implementations, e.g.,
        # on macOS.
        if platform.system() != "Linux":
            sleep(1.0)

    return _run_rule
