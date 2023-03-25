import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dry_run(tmp_path, run, init_tmp_path):
    """Test that using '--dry-run' causes the recipes not to be run."""
    girdfile = init_tmp_path(pytest_tmp_path=tmp_path, test_dir=TEST_DIR)

    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target"

    path_dep.touch()

    args = [
        "gird",
        "--girdfile",
        str(girdfile.resolve()),
        "target",
        "--dry-run",
    ]

    process = run(tmp_path, args)

    assert "create_target()" in process.stdout

    assert not path_target.exists()
