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
class FormattedRule:
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
        rules_formatted_makefile1,
        rules_formatted_makefile2,
    ) = format_rules(rules)
    for rules_formatted, path_makefile in zip(
        (rules_formatted_makefile1, rules_formatted_makefile2),
        (path_makefile1, path_makefile2),
    ):
        makefile_contents = get_makefile_contents(rules_formatted)
        path_makefile.write_text(makefile_contents)


def get_makefile_contents(rules: List[FormattedRule]) -> str:
    """Get contents of a full Makefile."""
    rules_makefile = [get_makefile_rule(rule) for rule in rules]
    contents = "\n\n".join(rules_makefile) + "\n"
    return contents


def get_makefile_rule(rule: FormattedRule) -> str:
    """Get a Makefile entry for a single rule."""
    parts = []

    if isinstance(rule.target, Phony):
        parts.append(f".PHONY: {rule.target}\n")

    parts.append(f"{rule.target}:")

    if rule.deps is not None:
        parts.extend(f" {dep}" for dep in rule.deps)

    if rule.recipe is not None:
        recipe_makefile = " && ".join(subprecipe for subprecipe in rule.recipe)
        parts.append("\n\t" + recipe_makefile)

    rule_makefile = "".join(parts)

    return rule_makefile


def format_rules(
    rules: Iterable[Rule],
) -> Tuple[List[FormattedRule], List[FormattedRule]]:
    """Convert Rules as FormattedRules, one set for both Makefile1 & Makefile2."""
    rules_formatted_makefile1 = []
    rules_formatted_makefile2 = []

    for dep_function in get_dep_functions(rules):
        rules_formatted_makefile1.append(
            format_dep_function_rule_makefile1(dep_function)
        )

    for rule in rules:
        rules_formatted_makefile1.extend(format_rule_makefile1(rule))
        rules_formatted_makefile2.append(format_rule_makefile2(rule))
    return rules_formatted_makefile1, rules_formatted_makefile2


def get_dep_functions(rules: Iterable[Rule]) -> List[DependencyFunction]:
    """Get a list of unique DependencyFunction instances used in the given Rules."""
    dep_functions = []
    for rule in rules:
        if rule.deps is not None:
            for dep in rule.deps:
                if isinstance(dep, DependencyFunction) and dep not in dep_functions:
                    dep_functions.append(dep)
    return dep_functions


def format_dep_function_rule_makefile1(
    dep_function: DependencyFunction,
) -> FormattedRule:
    """Convert a DependencyFunction as a FormattedRule for Makefile1."""
    return FormattedRule(
        target=format_path(dep_function.tag_path),
        deps=None,
        recipe=[get_python_function_shell_command(dep_function.function)],
    )


def format_rule_makefile1(rule: Rule) -> Tuple[FormattedRule, FormattedRule]:
    """Convert Rule as two FormattedRules for Makefile1."""
    rule_deps = create_deps_rule_makefile1(rule)

    target = Phony(format_target(rule.target))
    makefile2_path = format_path(get_gird_path_tmp() / "Makefile2")
    recipe = f"$(MAKE) --file {makefile2_path} {target}"
    rule_main = FormattedRule(
        target=target,
        deps=[rule_deps.target],
        recipe=[recipe],
    )

    return rule_main, rule_deps


def create_deps_rule_makefile1(rule: Rule) -> FormattedRule:
    """Create a FormattedRule for dependency propagation in Makefile1."""

    def format_target_for_deps_rule(target: Target) -> Phony:
        return Phony(str(format_target(target)) + "__deps")

    target = format_target_for_deps_rule(rule.target)

    deps = []
    if rule.deps is not None:
        for dep in rule.deps:
            if isinstance(dep, DependencyFunction):
                deps.append(format_path(dep.tag_path))
            elif isinstance(dep, Rule):
                deps.append(format_target_for_deps_rule(dep.target))
    deps = deps or None

    rule_formatted = FormattedRule(
        target=target,
        deps=deps,
        recipe=None,
    )

    return rule_formatted


def format_rule_makefile2(rule: Rule) -> FormattedRule:
    """Convert Rule as FormattedRule for Makefile2."""
    target = format_target(rule.target)

    deps = None
    if rule.deps is not None:
        deps = [format_dep_makefile2(dep) for dep in rule.deps]

    recipe = None
    if rule.recipe is not None:
        recipe = format_recipe_makefile2(rule.recipe)

    rule_formatted = FormattedRule(
        target=target,
        deps=deps,
        recipe=recipe,
    )

    return rule_formatted


def format_target(target: Target) -> Union[str, Phony]:
    """Format target for a Makefile."""
    if isinstance(target, Phony):
        target_formatted = target
    elif isinstance(target, pathlib.Path):
        target_formatted = format_path(target)
    else:
        raise NotImplementedError(f"Unsupported target type '{type(target)}'.")
    return target_formatted


def format_dep_makefile2(dep: Dependency) -> str:
    """Format a Dependency for Makefile2."""
    if isinstance(dep, pathlib.Path):
        dep_formatted = format_path(dep)
    elif isinstance(dep, Rule):
        dep_formatted = format_target(dep.target)
    elif isinstance(dep, DependencyFunction):
        dep_formatted = format_path(dep.tag_path)
    else:
        raise TypeError(f"Unsupported dependency type '{type(dep)}'.")
    return dep_formatted


def format_recipe_makefile2(recipe: Iterable[SubRecipe]) -> List[str]:
    """Format a recipe for Makefile2."""
    subrecipes_formatted = []
    for subrecipe in recipe:
        if isinstance(subrecipe, str):
            subrecipes_formatted.extend(subrecipe.split("\n"))
        elif isinstance(subrecipe, Callable):
            subrecipes_formatted.append(get_python_function_shell_command(subrecipe))
        else:
            raise TypeError(f"Unsupported recipe type '{type(subrecipe)}'.")
    return subrecipes_formatted


def format_path(path: pathlib.Path) -> str:
    """Format/normalize a Path to be relative to gird_path_run."""
    gird_path_run = get_gird_path_run()
    return os.path.relpath(path, gird_path_run)
