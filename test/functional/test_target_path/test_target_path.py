import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_target_path_with_dep(tmp_path, run_rule):
    """Test that for a Path target with a Path dependency,
    - the recipe is not run if it's dependency is not updated after the target
      is created, and
    - the recipe is run if the dependency is updated.
    """
    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target_with_dep"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_with_dep",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_with_dep",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second

    path_dep.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_with_dep",
    )

    mtime_third = path_target.stat().st_mtime_ns

    assert mtime_second < mtime_third


def test_target_path_without_dep(tmp_path, run_rule):
    """Test that for a Path target without a path dependency,
    - the recipe is run when the target doesn't exist, and
    - the recipe is not run when the target exists.
    """
    path_target = tmp_path / "target_without_dep"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_without_dep",
    )

    assert path_target.exists()

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target_without_dep",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second
