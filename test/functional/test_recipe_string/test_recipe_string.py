import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test_recipe_string(tmp_path, process_girdfile):
    """Test that a function recipe is properly run."""
    path_target = tmp_path / "target"

    process_girdfile(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    assert path_target.exists()
