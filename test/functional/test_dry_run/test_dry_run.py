import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dry_run(tmp_path, run_rule):
    """Test that using '--dry-run' causes the recipes not to be run."""
    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target"

    path_dep.touch()

    process = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
        dry_run=True,
    )

    assert (
        "python -c 'from girdfile import create_target; create_target()"
        in process.stdout
    )

    assert not path_target.exists()
