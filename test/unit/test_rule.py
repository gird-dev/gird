import pathlib

import pytest

from gird import Phony
from gird.rule import rule


def test_types():
    rule(target=Phony("target"))
    rule(target=pathlib.Path("target"))

    with pytest.raises(TypeError, match="Invalid target type: 'target'"):
        rule(target="target")

    dummy_rule_dep = rule(target=Phony("target"))

    def dummy_function_dep():
        return False

    rule(target=Phony("target"), deps=None)

    rule(target=Phony("target"), deps=pathlib.Path("dep"))
    rule(target=Phony("target"), deps=dummy_rule_dep)
    rule(target=Phony("target"), deps=dummy_function_dep)

    rule(target=Phony("target"), deps=[pathlib.Path("dep")])
    rule(target=Phony("target"), deps=[dummy_rule_dep])
    rule(target=Phony("target"), deps=[dummy_function_dep])

    with pytest.raises(TypeError, match="Invalid deps type: 'd'."):
        rule(target=Phony("target"), deps="deps")

    with pytest.raises(TypeError, match="Invalid deps type: 'deps'."):
        rule(target=Phony("target"), deps=["deps"])

    def dummy_function_recipe():
        pass

    rule(target=Phony("target"), recipe="recipe")
    rule(target=Phony("target"), recipe=dummy_function_recipe)

    rule(target=Phony("target"), recipe=["recipe"])
    rule(target=Phony("target"), recipe=[dummy_function_recipe])

    with pytest.raises(TypeError, match="Invalid recipe type: '1'."):
        rule(target=Phony("target"), recipe=1)

    with pytest.raises(TypeError, match="Invalid recipe type: '1'."):
        rule(target=Phony("target"), recipe=[1])
