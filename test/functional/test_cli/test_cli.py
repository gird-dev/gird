import pathlib
import shutil
from typing import List


def init_cli_test(pytest_tmp_path) -> List[str]:
    """Initialize pytest_tmp_path for the CLI tests. Return optional arguments
    to be used in all CLI tests.
    """
    # Use unconventionally named girdfile & gird_path in all the tests to make
    # sure everything works with those.
    path_girdfile_original = pathlib.Path(__file__).parent / "girdfile2.py"
    path_girdfile = pytest_tmp_path / path_girdfile_original.name
    gird_path = pytest_tmp_path / ".gird2"
    shutil.copy(path_girdfile_original, path_girdfile)
    args = [
        "gird",
        "--girdfile",
        str(path_girdfile.resolve()),
        "--girdpath",
        str(gird_path.resolve()),
    ]
    return args


def test_cli_no_girdfile(tmp_path, run):
    """Test functionality with nonexistent girdfile given as argument."""
    girdfile_name = "nonexistent-girdfile.py"
    process = run(
        tmp_path,
        ["gird", "--girdfile", girdfile_name],
        raise_on_error=False,
    )
    assert process.returncode == 1
    assert process.stderr.startswith(
        f"gird: Error: Could not import girdfile '{girdfile_name}'."
    )


def test_cli_help(tmp_path, run):
    """Test CLI argument --help."""
    # Test with nonexistent girdfile.
    process = run(
        tmp_path,
        ["gird", "--help"],
        raise_on_error=False,
    )
    assert process.stdout.startswith("usage: gird")

    # Test with an existing girdfile.
    args = init_cli_test(tmp_path)
    args.append("--help")
    process = run(
        tmp_path,
        args,
    )
    assert process.stdout.startswith("usage: gird")


def test_cli_no_arguments(tmp_path, run):
    """Test CLI with no arguments."""
    # Test with nonexistent girdfile.
    process = run(
        tmp_path,
        ["gird"],
        raise_on_error=False,
    )
    assert process.stdout.startswith("usage: gird")

    # Test with an existing girdfile.
    args = init_cli_test(tmp_path)
    process = run(
        tmp_path,
        args,
    )
    assert process.stdout.startswith("usage: gird")


def test_cli_verbose(tmp_path, run):
    """Test CLI argument --verbose."""
    args = init_cli_test(tmp_path)
    args.extend(["--verbose", "target"])
    run(
        tmp_path,
        args,
    )


def test_cli_list(tmp_path, run):
    """Test CLI subcommand 'list'."""
    # Test with nonexistent girdfile.
    process = run(
        tmp_path,
        ["gird", "list"],
        raise_on_error=False,
    )
    assert process.returncode == 1
    assert process.stderr.startswith(
        "gird: Error: Could not import girdfile 'girdfile.py'."
    )

    args = init_cli_test(tmp_path)
    args.append("list")
    process = run(
        tmp_path,
        args,
    )
    rule_listing = """target
    Create
    target.
"""
    assert process.stdout.startswith(rule_listing)


def test_cli_run_rule(tmp_path, run):
    """Test running a rule."""
    args = init_cli_test(tmp_path)
    args.append("target")
    run(
        tmp_path,
        args,
    )

    # Check that rule was run.
    path_target = tmp_path / "target"
    assert path_target.exists()

    # Check that .gird2 was used as gird_path.
    gird_path = tmp_path / ".gird2"
    assert len(list(gird_path.iterdir())) > 0


def test_cli_run_rule_with_error(tmp_path, run):
    """Test running a rule that causes an error."""
    args = init_cli_test(tmp_path)
    target = "target_with_error"
    args.append(target)
    process = run(
        tmp_path,
        args,
        raise_on_error=False,
    )
    assert process.returncode == 2
    assert (
        process.stderr.strip()
        .split("\n")[-1]
        .startswith(f"gird: Error: Execution of rule '{target}' returned with error.")
    )
