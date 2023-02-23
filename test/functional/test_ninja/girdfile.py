import datetime
import pathlib

import gird

rule_format = gird.rule(
    target=pathlib.Path("file0"),
    recipe=(
        r"""echo 'line1\n' >> file0
echo 'line2\n' >> file0"""
    ),
)

rule_test = gird.rule(
    target=gird.Phony("test"),
    recipe="echo 'Test succeeded.'",
    help="Run tests.",
)

rule_build = gird.rule(
    target=pathlib.Path("package.whl"),
    deps=pathlib.Path("source.py"),
    recipe="buildtool --format wheel",
    help="Build.",
)

gird.rule(
    target=gird.Phony("all"),
    deps=[rule_test, rule_build],
    help=f"""- {rule_test.help}
- {rule_build.help}""",
)

PATH_TARGET1 = pathlib.Path("file1")
PATH_TARGET2 = pathlib.Path("file2")
PATH_TARGET3 = pathlib.Path("file3")
PATH_TARGET4 = pathlib.Path("file4")


def create_target2():
    PATH_TARGET2.write_text("line2\n")


def create_target3():
    PATH_TARGET3.write_text(PATH_TARGET1.read_text() + PATH_TARGET2.read_text())


@gird.dep
def function_dep():
    return datetime.datetime.now() < datetime.datetime(2030, 1, 1)


rule_target1 = gird.rule(
    target=PATH_TARGET1,
    deps=[function_dep],
    recipe=f"echo 'line1' > {PATH_TARGET1.name}",
)

rule_target2 = gird.rule(
    target=PATH_TARGET2,
    deps=[function_dep],
    recipe=create_target2,
)

rule_target3 = gird.rule(
    target=PATH_TARGET3,
    deps=[rule_target1, rule_target2],
    recipe=create_target3,
)


rule_target4 = gird.rule(
    target=PATH_TARGET4,
    deps=[rule_target3],
    recipe=f"touch {PATH_TARGET4.name}",
)
