import gird

rule_pytest = gird.rule(
    target=gird.Phony("pytest"),
    recipe="pytest",
)

gird.rule(
    target=gird.Phony("tests"),
    deps=[
        rule_pytest,
    ],
)
