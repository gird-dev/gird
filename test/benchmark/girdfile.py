import pathlib

from tmp.targets import TARGET_COUNT

from gird import Phony, rule

DIR_TARGETS = pathlib.Path(__file__).parent / ".cache"

TARGETS = [DIR_TARGETS / f"file{i}" for i in range(TARGET_COUNT)]


rule(
    target=DIR_TARGETS,
    recipe=f"mkdir -p {DIR_TARGETS}",
)


for target in TARGETS:
    rule(
        target=target,
        recipe=f"touch {target}",
        deps=DIR_TARGETS,
        listed=False,
    )


rule(
    target=Phony("all"),
    deps=TARGETS,
)
