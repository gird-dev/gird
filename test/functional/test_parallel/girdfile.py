import pathlib
import time

import gird

TARGET1 = pathlib.Path("target1")
TARGET2 = pathlib.Path("target2")
TARGET3 = pathlib.Path("target3")
TARGET4 = pathlib.Path("target4")


def create_target(path: pathlib.Path):
    """Record current time twice in a file. Use time.sleep() to make sure the
    same times, with a precision of 0.1 seconds, couldn't be recorded without
    parallel execution.
    """
    print(f"{path} time0.")
    time0 = time.time()
    # Make sure the times are different with 0.1 second precision.
    time.sleep(0.101)
    print(f"{path} time1.")
    time1 = time.time()
    path.write_text(f"{time0}\n{time1}\n")
    # Make sure the same times won't be recorded in following invocations.
    time.sleep(0.101)


def create_target1():
    create_target(TARGET1)


def create_target2():
    create_target(TARGET2)


def create_target3():
    create_target(TARGET3)


def create_target4():
    create_target(TARGET4)


gird.rule(
    target=TARGET1,
    recipe=create_target1,
)


gird.rule(
    target=TARGET2,
    recipe=create_target2,
)


gird.rule(
    target=TARGET3,
    recipe=create_target3,
    parallel=False,
)


gird.rule(
    target=TARGET4,
    recipe=create_target4,
    parallel=False,
)


gird.rule(
    target=gird.Phony("parallel"),
    deps=[TARGET1, TARGET2],
)


gird.rule(
    target=gird.Phony("serial"),
    deps=[TARGET3, TARGET4],
)
