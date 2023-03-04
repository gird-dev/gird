import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_target_path(tmp_path, run_rule):
    """Test that the recipe of a Path target is not run if it's dependency is
    not updated after the target is created, and that the recipe is run if the
    dependency is updated.
    """
    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second

    path_dep.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    mtime_third = path_target.stat().st_mtime_ns

    assert mtime_second < mtime_third
