import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_rule_phony(tmp_path, process_girdfile):
    """Test that a recipe is always run if its rule has a rule dependency with a
    phony target.
    """
    path_target = tmp_path / "target"

    process_girdfile(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_first = path_target.stat().st_mtime_ns

    process_girdfile(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first < mtime_second
