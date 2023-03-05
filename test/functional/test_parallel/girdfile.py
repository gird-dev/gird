import pathlib
import time

import gird

TARGET1 = pathlib.Path("target1")
TARGET2 = pathlib.Path("target2")


def create_target(path: pathlib.Path):
    """Record current time twice in a file. Use time.wait() to make sure the
    same times, with a precision of on second, couldn't be recorded without
    parallel execution.
    """
    print(f"{path} time0.")
    time0 = time.time()
    time.sleep(0.51)
    print(f"{path} time1.")
    time1 = time.time()
    path.write_text(f"{time0}\n{time1}\n")
    time.sleep(1.01)


def create_target1():
    create_target(TARGET1)


def create_target2():
    create_target(TARGET2)


gird.rule(
    target=TARGET1,
    recipe=create_target1,
)


gird.rule(
    target=TARGET2,
    recipe=create_target2,
)


gird.rule(
    target=gird.Phony("parallel"),
    deps=[TARGET1, TARGET2],
)
