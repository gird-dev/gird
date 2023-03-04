import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_function_false(tmp_path, run_rule):
    """Test that a recipe is not run if a dependency function returns False and
    the target exists.
    """
    path_target = tmp_path / "target_false"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_false",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_false",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second


def test_dep_function_true(tmp_path, run_rule):
    """Test that a recipe is run if a dependency function returns True and
    the target exists.
    """
    path_target = tmp_path / "target_true"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_true",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_true",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first < mtime_second
