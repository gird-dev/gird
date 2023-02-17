import pathlib
import shutil
import subprocess


def test(tmp_path, run):
    """Test CLI arguments.
    - girdfile
    - girddir
    - list
    - verbose
    - target
    """
    # Use unconventionally named girdfile & girddir.
    path_girdfile_original = pathlib.Path(__file__).parent / "girdfile2.py"
    path_girdfile = tmp_path / "girdfile2.py"
    girddir = tmp_path / ".gird2"

    shutil.copy(path_girdfile_original, path_girdfile)

    path_target = tmp_path / "target"

    args = [
        "gird",
        "--girdfile",
        path_girdfile.resolve(),
        "--girddir",
        girddir.resolve(),
        "--list",
        "--verbose",
        "target",
    ]

    process = run(
        tmp_path,
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    stdout = process.stdout

    # Check that target was run.
    assert path_target.exists()

    # Check that .gird2 was used as girddir.
    assert len(list(girddir.iterdir())) > 0

    # Check effects of --list.
    targets_listing = """Targets:
    target
        Create
        target.
"""
    assert stdout.startswith(targets_listing)

    # Check effects of --verbose.
    verbose_output = stdout[len(targets_listing) :]
    assert verbose_output.startswith("make: Entering directory")
