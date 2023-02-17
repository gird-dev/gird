import pathlib

TEST_DIR = pathlib.Path(__file__).parent


def test(tmp_path, process_girdfile):
    process_girdfile(
        pytest_tmp_dir=tmp_path,
        test_dir=TEST_DIR,
        target="file4",
    )

    path_file1 = tmp_path / "file1"
    path_file2 = tmp_path / "file2"
    path_file3 = tmp_path / "file3"
    path_file4 = tmp_path / "file4"

    assert path_file1.read_text() == "line1\n"
    assert path_file2.read_text() == "line2\n"
    assert path_file3.read_text() == "line1\nline2\n"
    assert path_file4.exists()
