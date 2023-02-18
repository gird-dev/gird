import pathlib
import shutil
import subprocess


def test(tmp_path, run):
    """Test CLI arguments.
    - girdfile
    - girdpath
    - list
    - verbose
    - target
    """
    # Use unconventionally named girdfile & gird_path.
    path_girdfile_original = pathlib.Path(__file__).parent / "girdfile2.py"
    path_girdfile = tmp_path / "girdfile2.py"
    gird_path = tmp_path / ".gird2"

    shutil.copy(path_girdfile_original, path_girdfile)

    path_target = tmp_path / "target"

    args = [
        "gird",
        "--girdfile",
        path_girdfile.resolve(),
        "--girdpath",
        gird_path.resolve(),
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

    # Check that .gird2 was used as gird_path.
    assert len(list(gird_path.iterdir())) > 0

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
