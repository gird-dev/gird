import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_rule_phony(tmp_path, run_rule):
    """Test that a recipe is always run if its rule has a rule dependency with a
    phony target.
    """
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

    assert mtime_first < mtime_second
