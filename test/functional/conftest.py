import os
import pathlib
import shutil
import subprocess
from typing import Optional

import pytest


@pytest.fixture
def run():
    def _run(pytest_tmp_dir: pathlib.Path, *args, **kwargs):
        """Helper function for using subprocess.run in Pytest tmp_path.

        Parameters
        ----------
        pytest_tmp_dir
            Temporary directory to run a test in. Will be added to PYTHONPATH
            environment variable, and used as cwd in the subprocess.run call.
        args
            Positional arguments for subprocess.run.
        kwargs
            Keyword arguments for subprocess.run.
        """
        pythonpath = os.environ.get("PYTHONPATH", "")
        if pythonpath:
            pythonpath += os.pathsep
        pythonpath += str(pytest_tmp_dir.resolve())
        os.environ["PYTHONPATH"] = pythonpath

        return subprocess.run(
            *args,
            cwd=pytest_tmp_dir,
            **kwargs,
        )

    return _run


@pytest.fixture
def process_girdfile(run):
    def _process_girdfile(
        pytest_tmp_dir: pathlib.Path,
        test_dir: pathlib.Path,
        target: Optional[str] = None,
    ):
        """Process a girdfile.py.

        Parameters
        ----------
        pytest_tmp_dir
            Temporary directory to run this test in.
        test_dir
            Original test directory with girdfile.py. If the directory also
            contains files named Makefile1 & Makefile2, those will be compared
            to the Makefiles produced by Gird.
        target
            Name of the target to be run.
        """
        # Copy girdfile.py to pytest_tmp_dir.
        path_girdfile_original = test_dir / "girdfile.py"
        path_girdfile = pytest_tmp_dir / "girdfile.py"
        shutil.copy(path_girdfile_original, path_girdfile)

        girddir = pytest_tmp_dir / ".gird"
        girddir_tmp = girddir / "tmp"

        # First run with no target to assert Makefile contents.
        run(
            pytest_tmp_dir,
            ["gird"],
            check=True,
        )

        for makefile_name in ("Makefile1", "Makefile2"):
            path_makefile_target = test_dir / makefile_name
            path_makefile_result = girddir_tmp / makefile_name
            if path_makefile_target.exists():
                assert (
                    path_makefile_result.read_text() == path_makefile_target.read_text()
                )

        # Run also with target if one is specified.
        if target:
            run(
                pytest_tmp_dir,
                ["gird", target],
                check=True,
            )

    return _process_girdfile
