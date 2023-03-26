import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_object(tmp_path, run_rule):
    """Test that a custom class implementing the TimeTracked protocol can be
    used as a dependency.
    """
    target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    assert target.exists()
