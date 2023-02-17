import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_false(tmp_path, process_girdfile):
    """Test that a recipe is not run if a dependency function returns False and
    the target exists.
    """
    path_target = tmp_path / "target_false"

    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_first = path_target.stat().st_mtime_ns

    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="target_false",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first == mtime_second


def test_true(tmp_path, process_girdfile):
    """Test that a recipe is run if a dependency function returns True and
    the target exists.
    """
    path_target = tmp_path / "target_true"

    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="target_true",
    )

    mtime_first = path_target.stat().st_mtime_ns

    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="target_true",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first < mtime_second
