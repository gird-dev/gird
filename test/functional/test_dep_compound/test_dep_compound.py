import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_compound_false(tmp_path, run_rule):
    """Test that a recipe is run if any of the dependencies of its rule are
    updated.
    """
    path_dep_path = tmp_path / "dep_path"
    path_dep_rule = tmp_path / "dep_rule"
    path_target = tmp_path / "target_false"

    path_dep_path.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second

    path_dep_path.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_third = path_target.stat().st_mtime_ns

    assert mtime_second < mtime_third

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_fourth = path_target.stat().st_mtime_ns

    assert mtime_third == mtime_fourth

    path_dep_rule.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_fifth = path_target.stat().st_mtime_ns

    assert mtime_fourth < mtime_fifth

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_sixth = path_target.stat().st_mtime_ns

    assert mtime_fifth == mtime_sixth


def test_dep_compound_true(tmp_path, run_rule):
    """Test that a recipe is run if a dependency function returns True and
    the target exists, regardless of other dependencies.
    """
    path_dep_path = tmp_path / "dep_path"
    path_target = tmp_path / "target_true"

    path_dep_path.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_true",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target_true",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first < mtime_second
