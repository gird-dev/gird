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
        raise_on_error: bool = True,
        dry_run: bool = False,
        question: bool = False,
        output_sync: bool = False,
    ) -> subprocess.CompletedProcess:
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
        parallelism
            Parallelism state.
        dry_run
            Run Gird with '--dry-run'.
        question
            Run Gird with '--question'.
        """
        # Copy girdfile.py to pytest_tmp_path.
        path_girdfile_original = test_dir / "girdfile.py"
        # Use a unique name for the girdfile because the multiprocessing library
        # may get confused on some environments if names must be imported from
        # multiple modules with the same name.
        path_girdfile = pytest_tmp_path / f"girdfile_{test_dir.name}.py"
        shutil.copy(path_girdfile_original, path_girdfile)

        args = [
            "gird",
            "--girdfile",
            str(path_girdfile.resolve()),
        ]

        if output_sync:
            args.append("--output-sync")

        args.append(rule)

        if dry_run:
            args.append("--dry-run")

        if question:
            args.append("--question")

        process = run(
            pytest_tmp_path,
            args,
            raise_on_error=raise_on_error,
        )

        return process

    return _run_rule
