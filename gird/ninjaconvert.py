"""Code for formatting & writing Ninja build files.

Notes about the Ninja implementation.
- Ninja doesn't have similar support for phony targets. If a file with the name
  of a target exists, the target's rule won't be run.
- Ninja buffers all command output, preventing, e.g., Gird recipes that require
  user input.
- Ninja has a different rule definition scheme, which complicates the interface
  with Gird.

Gird uses two Ninja build files, build1.ninja & build2.ninja, to organize rules.
Functions in this module are postfixed with '_buildfile1' & '_buildfile2',
respectively.

The setup of two build files is used in order to handle dependencies defined as
Python functions.

The first build file, build1.ninja, contains build edges that 1) create tag
files based on dependencies defined as Python functions, 2) update targets in
the second build file, build2.ninja, as recursive Ninja invocations, or 3)
define dependencies between the build targets in the file.

The second build file, build2.ninja, contains the rules that execute the actual
recipes defined in the Gird rules. The targets in the file possibly depend on
the tag files created by the rules in the first build file.
"""

import dataclasses
import itertools
import os
import pathlib
from typing import Callable, Iterable, List, Optional, Tuple, Union

from .common import Dependency, Phony, Rule, SubRecipe, Target
from .dependency import DependencyFunction
from .girdpath import get_gird_path_run, get_gird_path_tmp
from .utils import get_python_function_shell_command


@dataclasses.dataclass
class FormattedRule:
    """A Rule with fields pre-formatted as strings for a build file."""

    target: str
    deps: Optional[Iterable[str]]
    recipe: Optional[Iterable[str]]


def write_buildfiles(rules: Iterable[Rule]):
    """Write build files based on Gird rules."""
    gird_path_tmp = get_gird_path_tmp()
    path_buildfile1 = gird_path_tmp / "build1.ninja"
    path_buildfile2 = gird_path_tmp / "build2.ninja"
    builddir1 = gird_path_tmp / "builddir1"
    builddir2 = gird_path_tmp / "builddir2"
    (
        rules_ninja1,
        rules_ninja2,
    ) = format_rules(rules)
    for ninja_rules, path_buildfile, builddir in zip(
        (rules_ninja1, rules_ninja2),
        (path_buildfile1, path_buildfile2),
        (builddir1, builddir2),
    ):
        buildfile_contents = format_buildfile_contents(ninja_rules, builddir)
        path_buildfile.write_text(buildfile_contents)


def format_buildfile_contents(
    rules: List[FormattedRule],
    builddir: pathlib.Path,
) -> str:
    """Format rules as contents of build file."""
    buildfile_contents = (
        f"builddir = {format_path(builddir)}\n\n"
        + "\n\n".join(entry for entry in format_buildfile_entries(rules))
        + "\n"
    )
    return buildfile_contents


def format_buildfile_entries(rules: Iterable[FormattedRule]) -> Iterable[str]:
    """Format single rule for build file."""
    rule_number = itertools.count(1)
    for rule in rules:
        parts = []

        if rule.recipe is not None:
            rule_name = f"rule_{next(rule_number)}"
            recipe = " && ".join(subprecipe for subprecipe in rule.recipe)
            parts.append(f"rule {rule_name}\n    command = {recipe}")
        else:
            rule_name = "phony"

        if rule.deps:
            deps = " " + " ".join(str(dep) for dep in rule.deps)
        else:
            deps = ""
        parts.append(f"build {rule.target}: {rule_name}{deps}")

        buildfile_entry = "\n".join(parts)

        yield buildfile_entry


def format_rules(
    rules: Iterable[Rule],
) -> Tuple[List[FormattedRule], List[FormattedRule]]:
    """Convert Rules as FormattedRules, one set for both buildfile1 & buildfile2."""
    rules_buildfile1 = []
    rules_buildfile2 = []

    for dep_function in get_dep_functions(rules):
        rules_buildfile1.append(convert_dep_function_rule_buildfile1(dep_function))

    for rule in rules:
        rules_buildfile1.extend(format_rule_buildfile1(rule))
        rules_buildfile2.append(format_rule_buildfile2(rule))
    return rules_buildfile1, rules_buildfile2


def get_dep_functions(
    rules: Iterable[Rule],
) -> List[DependencyFunction]:
    """Get a list of unique DependencyFunction instances used in the given Rules."""
    dep_functions = []
    for rule in rules:
        if rule.deps is not None:
            for dep in rule.deps:
                if isinstance(dep, DependencyFunction) and dep not in dep_functions:
                    dep_functions.append(dep)
    return dep_functions


def convert_dep_function_rule_buildfile1(
    dep_function: DependencyFunction,
) -> FormattedRule:
    """Convert a DependencyFunction as a FormattedRule for buildfile1."""
    return FormattedRule(
        target=format_path(dep_function.tag_path),
        deps=None,
        recipe=[get_python_function_shell_command(dep_function.function)],
    )


def format_rule_buildfile1(rule: Rule) -> List[FormattedRule]:
    """Convert Rule as FormattedRules for buildfile1."""
    rule_deps = create_deps_rule_buildfile1(rule)

    target = format_target(rule.target)
    buildfile2_path = format_path(get_gird_path_tmp() / "build2.ninja")
    recipe = f"ninja -f {buildfile2_path} {target}"
    rule_main = FormattedRule(
        target=target,
        deps=[rule_deps.target],
        recipe=[recipe],
    )

    return [rule_main, rule_deps]


def create_deps_rule_buildfile1(rule: Rule) -> FormattedRule:
    """Create a FormattedRule for dependency propagation in buildfile1."""

    def format_target_for_deps_rule(target: Target) -> str:
        return str(format_target(target)) + "__deps"

    target = format_target_for_deps_rule(rule.target)

    deps = []
    if rule.deps is not None:
        for dep in rule.deps:
            if isinstance(dep, DependencyFunction):
                deps.append(format_path(dep.tag_path))
            elif isinstance(dep, Rule):
                deps.append(format_target_for_deps_rule(dep.target))
    deps = deps or None

    formatted_rule = FormattedRule(
        target=target,
        deps=deps,
        recipe=None,
    )

    return formatted_rule


def format_rule_buildfile2(rule: Rule) -> FormattedRule:
    """Convert Rule as FormattedRule for buildfile2."""
    target = format_target(rule.target)

    deps = None
    if rule.deps is not None:
        deps = [format_dep_buildfile2(dep) for dep in rule.deps]

    recipe = None
    if rule.recipe is not None:
        recipe = format_recipe_buildfile2(rule.recipe)

    formatted_rule = FormattedRule(
        target=target,
        deps=deps,
        recipe=recipe,
    )

    return formatted_rule


def format_target(target: Target) -> Union[str, Phony]:
    """Format target for a buildfile."""
    if isinstance(target, Phony):
        formatted_target = target
    elif isinstance(target, pathlib.Path):
        formatted_target = format_path(target)
    else:
        raise NotImplementedError(f"Unsupported target type '{type(target)}'.")
    return formatted_target


def format_dep_buildfile2(dep: Dependency) -> str:
    """Format Dependency for buildfile2."""
    if isinstance(dep, pathlib.Path):
        formatted_dep = format_path(dep)
    elif isinstance(dep, Rule):
        formatted_dep = format_target(dep.target)
    elif isinstance(dep, DependencyFunction):
        dep_path = get_gird_path_tmp() / dep.name
        formatted_dep = format_path(dep_path)
    else:
        raise TypeError(f"Unsupported dependency type '{type(dep)}'.")
    return formatted_dep


def format_recipe_buildfile2(recipe: Iterable[SubRecipe]) -> List[str]:
    """Format recipe for buildfile2."""
    formatted_subrecipes = []
    for subrecipe in recipe:
        if isinstance(subrecipe, str):
            formatted_subrecipes.extend(subrecipe.split("\n"))
        elif isinstance(subrecipe, Callable):
            formatted_subrecipes.append(get_python_function_shell_command(subrecipe))
        else:
            raise TypeError(f"Unsupported recipe type '{type(subrecipe)}'.")
    return formatted_subrecipes


def format_path(path: pathlib.Path) -> str:
    """Format/normalize Path to be relative to gird_path_run."""
    gird_path_run = get_gird_path_run()
    return os.path.relpath(path, gird_path_run)
