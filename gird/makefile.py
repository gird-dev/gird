"""Code for formatting & writing Makefiles.

Gird uses two Makefiles, Makefile1 & Makefile2, to organize rules. Functions in
this module are postfixed with '_makefile1' & '_makefile2', respectively.

The setup of two Makefiles is used in order to handle dependencies defined as
Python functions.

Makefile1 contains only phony rules, and the recipes either 1) create tag files
based on dependencies defined as Python functions, or 2) run rules in Makefile2
as recursive Make invocations. Rules without a recipe are also created to
propagate dependencies between the phony rules.

Makefile2 contains rules that run the actual recipes defined as Gird rules. The
Makefile2 rules possibly depend on the tag files created by the rules in
Makefile1.
"""

import dataclasses
import os
import pathlib
from typing import Callable, Iterable, List, Optional, Tuple, Union

from .common import Dependency, Phony, Rule, SubRecipe, Target
from .dependency import DependencyFunction
from .girdpath import get_gird_path_run, get_gird_path_tmp
from .utils import get_python_function_shell_command


@dataclasses.dataclass
class MakefileRule:
    """A Rule with fields pre-formatted as strings for a Makefile."""

    target: Union[str, Phony]
    deps: Optional[Iterable[str]]
    recipe: Optional[Iterable[str]]


def write_makefiles(rules: Iterable[Rule]):
    """Write Makefiles based on a GirdfileDefinition."""
    makefile_dir = get_gird_path_tmp()
    path_makefile1 = makefile_dir / "Makefile1"
    path_makefile2 = makefile_dir / "Makefile2"
    (
        rules_makefile1,
        rules_makefile2,
    ) = convert_makefile_rules(rules)
    for makefile_rules, makefile_path in zip(
        (rules_makefile1, rules_makefile2),
        (path_makefile1, path_makefile2),
    ):
        makefile_contents = format_makefile(makefile_rules)
        makefile_path.write_text(makefile_contents)


def format_makefile(rules: List[MakefileRule]) -> str:
    """Format rules as a full Makefile."""
    makefile_contents = (
        ".ONESHELL:\n"
        + "\n"
        + "\n\n".join(format_makefile_rule(rule) for rule in rules)
        + "\n"
    )
    return makefile_contents


def format_makefile_rule(rule: MakefileRule) -> str:
    """Format a single rule for a Makefile."""
    parts = []

    if isinstance(rule.target, Phony):
        parts.append(f".PHONY: {rule.target}\n")

    parts.append(f"{rule.target}:")

    if rule.deps is not None:
        parts.extend(f" {dep}" for dep in rule.deps)

    if rule.recipe is not None:
        parts.append("\n")
        parts.append("\n".join(f"\t{subrecipe}" for subrecipe in rule.recipe))

    formatted_rule = "".join(parts)

    return formatted_rule


def convert_makefile_rules(
    rules: Iterable[Rule],
) -> Tuple[List[MakefileRule], List[MakefileRule]]:
    """Convert Rules as MakefileRules, one set for both Makefile1 & Makefile2."""
    rules_makefile1 = []
    rules_makefile2 = []

    for dep_function in get_dep_functions(rules):
        rules_makefile1.append(convert_dep_function_rule_makefile1(dep_function))

    for rule in rules:
        rules_makefile1.extend(convert_rule_makefile1(rule))
        rules_makefile2.append(convert_rule_makefile2(rule))
    return rules_makefile1, rules_makefile2


def get_dep_functions(rules: Iterable[Rule]) -> List[DependencyFunction]:
    """Get a list of unique DependencyFunction instances used in the given Rules."""
    dep_functions = []
    for rule in rules:
        if rule.deps is not None:
            for dep in rule.deps:
                if isinstance(dep, DependencyFunction) and dep not in dep_functions:
                    dep_functions.append(dep)
    return dep_functions


def convert_dep_function_rule_makefile1(
    dep_function: DependencyFunction,
) -> MakefileRule:
    """Convert a DependencyFunction as a MakefileRule for Makefile1."""
    return MakefileRule(
        target=Phony(dep_function.name),
        deps=None,
        recipe=[get_python_function_shell_command(dep_function.function)],
    )


def convert_rule_makefile1(rule: Rule) -> List[MakefileRule]:
    """Convert Rule as MakefileRules for Makefile1."""
    rule_deps = create_deps_rule_makefile1(rule)

    target = Phony(format_target(rule.target))
    makefile2_path = get_path_relative_to_gird_path_run(
        get_gird_path_tmp() / "Makefile2"
    )
    recipe = f"$(MAKE) --file {makefile2_path} {target}"
    rule_main = MakefileRule(
        target=target,
        deps=[rule_deps.target],
        recipe=[recipe],
    )

    return [rule_main, rule_deps]


def create_deps_rule_makefile1(rule: Rule) -> MakefileRule:
    """Create a MakefileRule for dependency propagation in Makefile1."""

    def format_target_for_deps_rule(target: Target) -> Phony:
        return Phony(format_target(target) + "__deps")

    target = format_target_for_deps_rule(rule.target)

    deps = []
    if rule.deps is not None:
        for dep in rule.deps:
            if isinstance(dep, DependencyFunction):
                deps.append(dep.name)
            elif isinstance(dep, Rule):
                deps.append(format_target_for_deps_rule(dep.target))
    deps = deps or None

    makefile_rule = MakefileRule(
        target=target,
        deps=deps,
        recipe=None,
    )

    return makefile_rule


def convert_rule_makefile2(rule: Rule) -> MakefileRule:
    """Convert Rule as MakefileRule for Makefile2."""
    target = format_target(rule.target)

    deps = None
    if rule.deps is not None:
        deps = [format_dep_makefile2(dep) for dep in rule.deps]

    recipe = None
    if rule.recipe is not None:
        recipe = format_recipe_makefile2(rule.recipe)

    makefile_rule = MakefileRule(
        target=target,
        deps=deps,
        recipe=recipe,
    )

    return makefile_rule


def format_target(target: Target) -> Union[str, Phony]:
    """Format target for a Makefile."""
    if isinstance(target, Phony):
        makefile_target = target
    elif isinstance(target, pathlib.Path):
        makefile_target = get_path_relative_to_gird_path_run(target)
    else:
        raise NotImplementedError(f"Unsupported target type '{type(target)}'.")
    return makefile_target


def format_dep_makefile2(dep: Dependency) -> str:
    """Format a Dependency for Makefile2."""
    if isinstance(dep, pathlib.Path):
        makefile_dep = get_path_relative_to_gird_path_run(dep)
    elif isinstance(dep, Rule):
        makefile_dep = format_target(dep.target)
    elif isinstance(dep, DependencyFunction):
        dep_path = get_gird_path_tmp() / dep.name
        makefile_dep = get_path_relative_to_gird_path_run(dep_path)
    else:
        raise TypeError(f"Unsupported dependency type '{type(dep)}'.")
    return makefile_dep


def format_recipe_makefile2(recipe: Iterable[SubRecipe]) -> List[str]:
    """Format a recipe for Makefile2."""
    subrecipes = []
    for subrecipe in recipe:
        if isinstance(subrecipe, str):
            subrecipes.extend(subrecipe.split("\n"))
        elif isinstance(subrecipe, Callable):
            subrecipes.append(get_python_function_shell_command(subrecipe))
        else:
            raise TypeError(f"Unsupported recipe type '{type(subrecipe)}'.")
    return subrecipes


def get_path_relative_to_gird_path_run(path: pathlib.Path) -> str:
    """Format/normalize a Path to be relative to gird_path_run."""
    gird_path_run = get_gird_path_run()
    return os.path.relpath(path, gird_path_run)
