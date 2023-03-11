import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_recipe_compound(tmp_path, run_rule):
    """Test that a compound recipe is properly run. Check that environment
    variables set by preceding subrecipes are accessible by function subrecipes,
    i.e., the subrecipes are run in a single shell instance.
    """
    path_target = tmp_path / "target"

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    assert path_target.exists()
    assert path_target.read_text() == "line1\nline2\n"
