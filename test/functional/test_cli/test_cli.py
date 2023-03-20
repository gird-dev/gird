import pathlib
import shutil
from typing import List

TEST_DIR = pathlib.Path(__file__).parent


def init_cli_test(pytest_tmp_path) -> List[str]:
    """Initialize pytest_tmp_path for the CLI tests. Return optional arguments
    to be used in all CLI tests.
    """
    path_girdfile_original = TEST_DIR / "girdfile.py"
    # Use subdirectory to test that also that works.
    path_run_dir = pytest_tmp_path / "run_dir"
    path_girdfile = path_run_dir / f"girdfile_{TEST_DIR.name}.py"
    path_run_dir.mkdir(exist_ok=True)
    shutil.copy(path_girdfile_original, path_girdfile)
    args = [
        "gird",
        "--girdfile",
        str(path_girdfile.resolve()),
    ]
    return args


def test_cli_no_girdfile(tmp_path, run):
    """Test functionality with nonexistent girdfile given as argument."""
    girdfile_name = "nonexistent_girdfile.py"
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
    assert process.stdout == rule_listing

    args = init_cli_test(tmp_path)
    args.extend(["list", "--all"])
    process = run(
        tmp_path,
        args,
    )
    rule_listing = """target
    Create
    target.
target_with_error1
target_with_error2
"""
    assert process.stdout == rule_listing

    args = init_cli_test(tmp_path)
    args.extend(["list", "--question"])
    process = run(
        tmp_path,
        args,
    )
    rule_listing = """* target
      Create
      target.
"""
    assert process.stdout == rule_listing


def test_cli_run(tmp_path, run):
    """Test running a rule."""
    args = init_cli_test(tmp_path)
    args.extend(["run", "target"])
    run(
        tmp_path,
        args,
    )

    # Check that rule was run.
    path_target = tmp_path / "run_dir" / "target"
    assert path_target.exists()


def test_cli_target(tmp_path, run):
    """Test running a rule."""
    args = init_cli_test(tmp_path)
    args.append("target")
    run(
        tmp_path,
        args,
    )

    # Check that rule was run.
    path_target = tmp_path / "run_dir" / "target"
    assert path_target.exists()


def test_cli_unexisting_target(tmp_path, run):
    """Test functionality with nonexistent target given as argument."""
    args = init_cli_test(tmp_path)
    target = "nonexistent_target"
    args.append(target)
    process = run(
        tmp_path,
        args,
        raise_on_error=False,
    )
    assert process.returncode == 1
    assert process.stderr.startswith(
        f"gird: Error: argument {{list, [run] target}}: invalid choice: '{target}'"
    )


def test_cli_run_rule_with_error(tmp_path, run):
    """Test running a rule that causes an error."""
    args = init_cli_test(tmp_path)

    target = "target_with_error1"
    args1 = args + [target]
    process = run(
        tmp_path,
        args1,
        raise_on_error=False,
    )
    assert process.returncode == 1
    assert process.stderr.startswith(f"gird: Error: Exception\n\n")

    target = "target_with_error2"
    args2 = args + [target]
    process = run(
        tmp_path,
        args2,
        raise_on_error=False,
    )
    assert process.returncode == 1
    assert process.stderr.startswith(
        f"gird: Error: Command 'exit 1' exited with error code 1.\n\n"
    )
