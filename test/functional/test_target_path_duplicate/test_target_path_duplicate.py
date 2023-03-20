import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_target_path_duplicate(tmp_path, run_rule):
    """Test that using the same target in two rules raises an error."""
    process = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
        raise_on_error=False,
    )

    assert process.returncode == 1
    assert process.stderr.startswith(
        "gird: Error: Could not import girdfile 'girdfile_test_target_path_duplicate.py'."
    )
