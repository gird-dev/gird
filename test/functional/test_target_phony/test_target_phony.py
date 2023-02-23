import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test(tmp_path, process_girdfile):
    """Test that the recipe of the phony target is every time the target is
    invoked.
    """
    path_result = tmp_path / "target"

    process_girdfile(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="phony_target",
    )

    mtime_first = path_result.stat().st_mtime_ns

    process_girdfile(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="phony_target",
    )

    mtime_second = path_result.stat().st_mtime_ns

    assert mtime_second > mtime_first
