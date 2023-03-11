import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_graph(tmp_path, run_rule):
    """Test that target dependency graph works correctly.
    - Test that a predecessor rule without the need to be updated is not
      updated.
    - Test that a non-predecessor rule is not updated, even if it's a
      successor of a predecessor that is updated.
    - Test that two outdated predecessors are both updated when their common
      successor is requested to be updated.
    """
    target1 = tmp_path / "target1"
    target2 = tmp_path / "target2"
    target3 = tmp_path / "target3"
    target4 = tmp_path / "target4"
    target5 = tmp_path / "target5"

    target1.touch()
    mtime_target1_first = target1.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target5",
    )

    mtime_target1_second = target1.stat().st_mtime_ns
    assert mtime_target1_first == mtime_target1_second

    assert target2.exists()
    assert target3.exists()
    assert not target4.exists()
    assert target5.exists()
