import pathlib

import pytest

TEST_DIR = pathlib.Path(__file__).parent


def test_target_path_duplicate(tmp_path, run_rule):
    """Test that using the same target in two rules raises an error."""
    with pytest.raises(
        ValueError,
        match="A Rule with the target name 'target' has already been registered.",
    ):
        run_rule(
            pytest_tmp_path=tmp_path,
            test_dir=TEST_DIR,
            target="target",
        )
