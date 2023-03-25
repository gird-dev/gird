import pathlib

from gird.gird import SubcommandResult

TEST_DIR = pathlib.Path(__file__).parent


def test_question(tmp_path, run_rule):
    """Test that --question feature works properly."""
    path_dep = tmp_path / "dep"

    path_dep.touch()

    # Test that the result doesn't change by doing twice.
    for _ in range(2):
        result = run_rule(
            pytest_tmp_path=tmp_path,
            test_dir=TEST_DIR,
            target="target",
            question=True,
        )

        assert result == SubcommandResult.QUESTION_OUTDATED

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    result = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
        question=True,
    )

    assert result == SubcommandResult.QUESTION_UPTODATE

    # Run once more without --question.
    result = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    assert result == SubcommandResult.RUN_UNNECESSARY
