import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_rule_path(tmp_path, run_rule):
    """Test that the recipe of a Rule with a Rule dependency, that has a Path
    as its target,
    - is not run if the Path target of a Rule dependency is not updated after
      the target is created, and
    - is run if the dependency is updated.
    """
    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second

    path_dep.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_third = path_target.stat().st_mtime_ns

    assert mtime_second < mtime_third
