import pathlib

import pytest

from gird import Phony
from gird.rule import rule as grule


def test_type_check():
    """Test that the type checks work properly."""
    grule(target=Phony("target"))
    grule(target=pathlib.Path("target"))

    with pytest.raises(TypeError, match="Invalid target type: 'target'"):
        grule(target="target")

    dummy_rule_dep = grule(target=Phony("dep"))

    def dummy_function_dep():
        return False

    grule(target=Phony("target"), deps=None)

    grule(target=Phony("target"), deps=pathlib.Path("dep"))
    grule(target=Phony("target"), deps=Phony("dep"))
    grule(target=Phony("target"), deps=dummy_rule_dep)
    grule(target=Phony("target"), deps=dummy_function_dep)

    grule(target=Phony("target"), deps=[pathlib.Path("dep")])
    grule(target=Phony("target"), deps=[Phony("dep")])
    grule(target=Phony("target"), deps=[dummy_rule_dep])
    grule(target=Phony("target"), deps=[dummy_function_dep])

    with pytest.raises(TypeError, match="Invalid deps type: 'd'."):
        grule(target=Phony("target"), deps="deps")

    with pytest.raises(TypeError, match="Invalid deps type: 'deps'."):
        grule(target=Phony("target"), deps=["deps"])

    def dummy_function_recipe():
        pass

    grule(target=Phony("target"), recipe="recipe")
    grule(target=Phony("target"), recipe=dummy_function_recipe)

    grule(target=Phony("target"), recipe=["recipe"])
    grule(target=Phony("target"), recipe=[dummy_function_recipe])

    with pytest.raises(TypeError, match="Invalid recipe type: '1'."):
        grule(target=Phony("target"), recipe=1)

    with pytest.raises(TypeError, match="Invalid recipe type: '1'."):
        grule(target=Phony("target"), recipe=[1])


def test_iterators():
    """Test that iterators are properly handled."""
    deps = [
        pathlib.Path("dep1"),
        pathlib.Path("dep2"),
    ]
    recipe = [
        "echo 1",
        "echo 2",
    ]
    rule = grule(target=Phony("target"), deps=iter(deps), recipe=iter(recipe))
    assert len(rule.deps) == 2
    assert len(rule.recipe) == 2
