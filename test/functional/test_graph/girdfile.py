from pathlib import Path

from gird import Phony, rule

SOURCE1 = Path("source1")
TARGET1 = Path("target1")
TARGET2 = Path("target2")
TARGET3 = Path("target3")
TARGET4 = Path("target4")


def dep_function():
    return True


RULE1 = rule(
    target=TARGET1,
    deps=SOURCE1,
    recipe=f"echo 'line1' > {TARGET1}",
)

rule(
    target=TARGET2,
    deps=[SOURCE1, dep_function],
    recipe=f"echo 'line2' > {TARGET2}",
)

rule(
    target=TARGET3,
    deps=[RULE1, TARGET2],
    recipe=f"cat {TARGET1} {TARGET2} > {TARGET3}",
    parallel=False,
)

rule(
    target=TARGET4,
    recipe=f"echo 'line3' > {TARGET4}",
)


def print_targets():
    print(TARGET3.read_text() + TARGET4.read_text())


rule(
    target=Phony("target5"),
    deps=[TARGET3, TARGET4],
    recipe=[
        # The shell command's output should be displayed in red.
        f'echo -e "\033[0;31m$(cat {TARGET3} {TARGET4})\033[0m"',
        print_targets,
    ],
)
