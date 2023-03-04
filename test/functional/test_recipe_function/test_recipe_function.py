import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_recipe_function(tmp_path, run_rule):
    """Test that a string recipe is properly run."""
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    assert path_target.exists()
