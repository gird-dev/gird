import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_question(tmp_path, run_rule):
    """Test that --question feature works properly."""
    path_dep = tmp_path / "dep"

    path_dep.touch()

    # Test that the result doesn't change by doing twice.
    for _ in range(2):
        process = run_rule(
            pytest_tmp_path=tmp_path,
            test_dir=TEST_DIR,
            rule="target",
            raise_on_error=False,
            question=True,
        )

        assert process.returncode == 1
        assert (
            process.stdout.strip()
            .split("\n")[-1]
            .startswith("gird: Rule 'target' is not up to date.")
        )

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    process = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
        question=True,
    )

    assert process.returncode == 0
    assert (
        process.stdout.strip()
        .split("\n")[-1]
        .startswith("gird: Rule 'target' is up to date.")
    )
