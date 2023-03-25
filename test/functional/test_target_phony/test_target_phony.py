import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_target_phony(tmp_path, run_rule):
    """Test that the recipe of a phony target is executed every time the rule
    is invoked.
    """
    path_result = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_first = path_result.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_second = path_result.stat().st_mtime_ns

    assert mtime_second > mtime_first
