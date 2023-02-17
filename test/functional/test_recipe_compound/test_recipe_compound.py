import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test(tmp_path, process_girdfile):
    """Test that a compound recipe is properly run. Check that environment
    variables set by preceding subrecipes are accessible by function subrecipes,
    i.e., the subrecipes are run in a single shell instance.
    """
    path_target = tmp_path / "target"

    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="target",
    )

    assert path_target.exists()
