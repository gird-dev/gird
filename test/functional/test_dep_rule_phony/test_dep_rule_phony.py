import pathlib

import pytest

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_rule_phony(tmp_path, run_rule):
    """Test that a recipe is always run if its rule has a rule dependency with a
    phony target.
    """
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_first = path_target.stat().st_mtime_ns

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_second = path_target.stat().st_mtime_ns

    assert mtime_first < mtime_second


def test_dep_rule_phony_no_rule(tmp_path, run_rule):
    """Test that using a Phony object, that is not the target of a Rule, as a
    dependency causes an Error.
    """
    with pytest.raises(
        TypeError,
        match="Phony target 'phony_no_rule' of no rule used as a dependency.",
    ):
        run_rule(
            pytest_tmp_path=tmp_path,
            test_dir=TEST_DIR,
            target="target_no_rule",
        )
