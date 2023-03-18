import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_recipe_function(tmp_path, run_rule):
    """Test that a function recipe is properly run."""
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule=path_target.name,
    )

    assert path_target.exists()


def test_recipe_function_partial(tmp_path, run_rule):
    """Test that a function recipe wrapped with functools.partial is properly
    run.
    """
    path_target = tmp_path / "target_partial"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule=path_target.name,
    )

    assert path_target.exists()


def test_recipe_function_local(tmp_path, run_rule):
    """Test that a locally defined function recipe is properly run if the rule
    is defined with parallel=False.
    """
    path_target = tmp_path / "target_local"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule=path_target.name,
    )

    assert path_target.exists()


def test_recipe_function_lambda(tmp_path, run_rule):
    """Test that a function recipe defined as a Lambda function is properly run
    if the rule is defined with parallel=False.
    """
    path_target = tmp_path / "target_lambda"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule=path_target.name,
    )

    assert path_target.exists()
