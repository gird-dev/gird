"""Module for managing & sorting Rules as a directed acyclic graph."""
import graphlib
import pathlib
from typing import Callable, Dict, Iterable, Mapping, Set

from .common import Phony, Rule, Target, format_target
from .utils import get_path_modified_time


class RuleSorter(graphlib.TopologicalSorter):
    def __init__(self, rules: Iterable[Rule], target: Target):
        """TopologicalSorter for sorting Rules to be run to update a target.

        The graph for the sorting is built with the function get_target_graph.

        The nodes of RuleSorter are formatted target names, given by
        .common.format_target.

        Parameters
        ----------
        rules
            The Rules defined in a girdfile.
        target
            The target to be updated.
        """
        target_formatted = format_target(target)
        self._map_target_rule = {format_target(rule.target): rule for rule in rules}
        self.graph = build_target_graph(self.map_target_rule, target_formatted)
        super().__init__(self.graph)

    def is_target_outdated(self) -> bool:
        """Is the given target outdated, i.e., are there any rules to be run."""
        return bool(self.graph)

    @property
    def map_target_rule(self) -> Dict[str, Rule]:
        """Mapping from formatted target names to their Rules."""
        return self._map_target_rule


def build_target_graph(
    map_target_rule: Mapping[str, Rule],
    target: str,
) -> Dict[str, Set[str]]:
    """Build a graph of rule target dependencies. Include only outdated targets.

    This function will call the dependency functions of the Rules that are
    dependencies for the target.

    See the function `gird.rule` for the cases when a target should be
    considered outdated.

    Parameters
    ----------
    map_target_rule
        Mapping from formatted target names to Rules defined in a girdfile.
    target
        The formatted target name of the target to be updated.

    Returns
    -------
    graph
        Mapping from formatted target names to dependency targets. Only such
        targets will be included that need to be updated to update the given
        target. The graph will be empty if there's nothing to update.
    """

    def build_graph(rule: Rule) -> Dict[str, Set[str]]:
        """Recursively build the target dependency graph."""

        if isinstance(rule.target, Phony):
            rule_is_outdated = True
        else:
            rule_is_outdated = not rule.target.exists()

        graph: Dict[str, Set[str]] = dict()
        predecessors: Set[str] = set()

        if rule.deps:
            for dep in rule.deps:
                if isinstance(dep, Callable):
                    rule_is_outdated |= dep()
                else:
                    if format_target(dep) in map_target_rule:
                        dep = map_target_rule[format_target(dep)]

                        dep_graph = build_graph(dep)
                        dep_is_outdated = bool(dep_graph)

                        if dep_is_outdated:
                            predecessors.add(format_target(dep.target))
                            graph.update(dep_graph)

                        rule_is_outdated |= dep_is_outdated

                        dep = dep.target
                    elif isinstance(dep, Phony):
                        raise TypeError(
                            f"Phony target '{format_target(dep)}' of no rule "
                            "used as a dependency."
                        )
                    elif isinstance(dep, pathlib.Path) and not dep.exists():
                        raise RuntimeError(
                            f"Nonexistent file '{dep}' used as a dependency "
                            f"is not the target of any rule."
                        )

                    if (
                        isinstance(rule.target, pathlib.Path)
                        and isinstance(dep, pathlib.Path)
                        and rule.target.exists()
                        and dep.exists()
                    ):
                        rule_is_outdated |= get_path_modified_time(
                            dep
                        ) > get_path_modified_time(rule.target)

        if rule_is_outdated:
            node = format_target(rule.target)
            graph[node] = predecessors

        return graph

    return build_graph(map_target_rule[target])
