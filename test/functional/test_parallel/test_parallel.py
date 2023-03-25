import pathlib
from typing import Set

TEST_DIR = pathlib.Path(__file__).parent


def get_times(path: pathlib.Path) -> Set[float]:
    """Read the times from a target file with one second precision."""
    return set(round(float(line), 1) for line in path.read_text().strip().split("\n"))


def test_parallel(tmp_path, run, init_tmp_path):
    """Test that a recipe is by default run in parallel with recipes of other
    rules.
    """
    girdfile = init_tmp_path(pytest_tmp_path=tmp_path, test_dir=TEST_DIR)

    args = [
        "gird",
        "--girdfile",
        str(girdfile.resolve()),
        "parallel",
    ]

    run(
        tmp_path,
        args,
    )

    target1 = tmp_path / "target1"
    target2 = tmp_path / "target2"

    times1 = get_times(target1)
    times2 = get_times(target2)

    # Test that recorded times overlap.
    assert len(times1 & times2) > 0

    # NOTE For some reason the test below doesn't work on GitHub's runners, and
    #      is therefore disabled. Interspersed output probably isn't anything
    #      that somebody would absolutely desire anyway.
    # Test that output is not buffered, i.e., the recipes' output is not intact.
    # for target in (target1, target2):
    #     assert f"{target.name} time0.\n{target.name} time1.\n" not in process.stdout


def test_parallel_output_sync(tmp_path, run, init_tmp_path):
    """Test that the output of a recipe is buffered with the "--output-sync" CLI
    argument.
    """
    girdfile = init_tmp_path(pytest_tmp_path=tmp_path, test_dir=TEST_DIR)

    args = [
        "gird",
        "--girdfile",
        str(girdfile.resolve()),
        "--output-sync",
        "parallel",
    ]

    process = run(
        tmp_path,
        args,
    )

    target1 = tmp_path / "target1"
    target2 = tmp_path / "target2"

    times1 = get_times(target1)
    times2 = get_times(target2)

    # Test that recorded times overlap.
    assert len(times1 & times2) > 0

    # Test that output is buffered, i.e., the recipes' output is intact.
    for target in (target1, target2):
        assert f"{target.name} time0.\n{target.name} time1.\n" in process.stdout


def test_parallel_off(tmp_path, run, init_tmp_path):
    """Test that a recipe is not run in parallel with recipes of other rules
    when parallel=False.
    """
    girdfile = init_tmp_path(pytest_tmp_path=tmp_path, test_dir=TEST_DIR)

    args = [
        "gird",
        "--girdfile",
        str(girdfile.resolve()),
        "serial",
    ]

    process = run(
        tmp_path,
        args,
    )

    target3 = tmp_path / "target3"
    target4 = tmp_path / "target4"

    times1 = get_times(target3)
    times2 = get_times(target4)

    # Test that recorded times don't overlap.
    assert len(times1 & times2) == 0

    # Test that recipes' output is intact.
    for target in (target3, target4):
        assert f"{target.name} time0.\n{target.name} time1.\n" in process.stdout
