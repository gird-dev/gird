import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_target_object(tmp_path, run_rule):
    """Test that a custom class implementing the TimeTracked protocol can be
    used as a target.
    """
    target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    assert target.exists()

    mtime_first = target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_second = target.stat().st_mtime_ns

    # The custom class always has exists=False, so it should have been created
    # again.
    assert mtime_second > mtime_first
