import pathlib
import subprocess
import sys
import time

import matplotlib.pyplot as plt

DIR_BENCHMARK = pathlib.Path(__file__).parent
DIR_CACHE = DIR_BENCHMARK / ".cache"
DIR_TMP = DIR_BENCHMARK / "tmp"
DIR_PYCACHE = DIR_BENCHMARK / "__pycache__"
PATH_TARGETS_MK = DIR_TMP / "targets.mk"
PATH_TARGETS_PY = DIR_TMP / "targets.py"


def remove_dir(dir: pathlib.Path):
    if not dir.exists():
        return

    for path in dir.iterdir():
        path.unlink()
    dir.rmdir()


def benchmark_make():
    DIR_TMP.mkdir(exist_ok=True)

    target_counts = [1, 500, 1000]
    time_diffs = []
    for target_count in target_counts:
        remove_dir(DIR_CACHE)
        targets_str = " ".join(f"{DIR_CACHE.name}/file{i}" for i in range(target_count))
        PATH_TARGETS_MK.write_text(f"targets = {targets_str}")
        t0 = time.time()
        subprocess.run("make -j all --silent", shell=True, cwd=DIR_BENCHMARK)
        t1 = time.time()
        time_diffs.append(t1 - t0)

    plt.plot(target_counts, time_diffs, label="make")


def benchmark_gird(python_bin_path: pathlib.Path):
    path_python = python_bin_path / "python"
    path_gird = python_bin_path / "gird"

    DIR_TMP.mkdir(exist_ok=True)

    target_counts = [1, 500, 1000]
    time_diffs = []
    for target_count in target_counts:
        remove_dir(DIR_PYCACHE)
        remove_dir(DIR_CACHE)
        PATH_TARGETS_PY.write_text(f"TARGET_COUNT = {target_count}")
        t0 = time.time()
        subprocess.run(
            f"{path_python} {path_gird} run all", shell=True, cwd=DIR_BENCHMARK
        )
        t1 = time.time()
        time_diffs.append(t1 - t0)

    python_version = (
        subprocess.run(
            f"{path_python} --version",
            shell=True,
            capture_output=True,
            text=True,
        )
        .stdout.split(" ")[1]
        .strip()
    )

    plt.plot(target_counts, time_diffs, label=f"gird, python {python_version}")


def main():
    bin_dirs = sys.argv[1:]
    if not bin_dirs:
        print(
            "This script expects Python environments bin directories as optional "
            "arguments."
        )
    for bin_dir in bin_dirs:
        benchmark_gird(pathlib.Path(bin_dir))
    benchmark_make()

    plt.legend(loc=2)
    plt.xlabel("Number of files")
    plt.ylabel("Duration, seconds")
    plt.xlim(-10, 1010)
    plt.ylim(0)

    plt.show()


if __name__ == "__main__":
    main()
