import pathlib

import pytest

TEST_DIR = pathlib.Path(__file__).parent


def test_dep_path(tmp_path, run_rule):
    """Test that the recipe of a Rule with a Path dependency, that is not the
    target of another rule,
    - is not run if a Path dependency is not updated after the target is
      created, and
    - is run if the dependency is updated.
    """
    path_dep = tmp_path / "dep"
    path_target = tmp_path / "target"

    path_dep.touch()

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

    assert mtime_first == mtime_second

    path_dep.touch()

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    mtime_third = path_target.stat().st_mtime_ns

    assert mtime_second < mtime_third


def test_dep_path_nonexistent(tmp_path, run_rule):
    """Test that running the Rule with a Path dependency, that is not the
    target of another rule, raises an Error if the dependency doesn't exist.
    """
    with pytest.raises(
        RuntimeError,
        match="Nonexistent file 'dep' used as a dependency is not the target of any rule.",
    ):
        run_rule(
            pytest_tmp_path=tmp_path,
            test_dir=TEST_DIR,
            target="target",
        )
