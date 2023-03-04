import pathlib
import shutil

TEST_DIR = pathlib.Path(__file__).parent


def test_girdfile_import(tmp_path, run_rule):
    """Test that girdfile import works, and imports from the girdfile work."""
    path_target = tmp_path / "target"

    path_package_init_original = TEST_DIR / "package" / "__init__.py"
    path_package_init = tmp_path / "package" / "__init__.py"

    path_package_init.parent.mkdir()
    shutil.copy(path_package_init_original, path_package_init)

    run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="target",
    )

    assert path_target.exists()
