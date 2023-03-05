import pathlib
from typing import Set

from gird.common import PARALLELISM_UNLIMITED_JOBS

TEST_DIR = pathlib.Path(__file__).parent


def get_times(path: pathlib.Path) -> Set[int]:
    """Read the times from a target file with one second precision."""
    return set(int(round(float(line))) for line in path.read_text().strip().split("\n"))


def test_parallel(tmp_path, run_rule):
    """Test that a recipe is run in parallel."""
    process = run_rule(
        pytest_tmp_path=tmp_path,
        test_dir=TEST_DIR,
        rule="parallel",
        parallelism=PARALLELISM_UNLIMITED_JOBS,
    )

    target1 = tmp_path / "target1"
    target2 = tmp_path / "target2"

    times1 = get_times(target1)
    times2 = get_times(target2)

    # Test that recorded times overlap.
    assert len(times1 & times2) > 0

    # Test that output is buffered, i.e., recipes' output is intact.
    for target in (target1, target2):
        assert f"{target.name} time0.\n{target.name} time1.\n" in process.stdout
