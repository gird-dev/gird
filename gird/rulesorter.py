"""Module for managing & sorting Rules as a directed acyclic graph."""
import graphlib
from typing import Iterable, Mapping

from .common import Rule, Target
from .object import Phony


class RuleSorter(graphlib.TopologicalSorter):
    def __init__(self, rules: Iterable[Rule], target: Target):
        """TopologicalSorter for sorting Rules to be run to update a target.

        The graph for the sorting is built with the function get_target_graph.

        The nodes of RuleSorter are the ids of the targets.

        A RuleSorter instance will prepare itself upon initialization. The
        prepare method doesn't need to be called.

        Parameters
        ----------
        rules
            The Rules defined in a girdfile.
        target
            The target to be updated.
        """
        self._map_target_rule = {rule.target.id: rule for rule in rules}
        self.graph = build_target_graph(self.map_target_rule, target)
        super().__init__(self.graph)
        self.prepare()

    def is_target_outdated(self) -> bool:
        """Is the given target outdated, i.e., are there any rules to be run."""
        return bool(self.graph)

    @property
    def map_target_rule(self) -> dict[str, Rule]:
        """Mapping from target ids to their Rules."""
        return self._map_target_rule


def build_target_graph(
    map_target_rule: Mapping[str, Rule],
    target: Target,
) -> dict[str, set[str]]:
    """Build a graph of rule target dependencies. Include only outdated targets.

    This function will call the dependency functions that are either direct or
    indirect dependencies for the target.

    See the function `gird.rule` for the cases when a target should be
    considered outdated.

    Parameters
    ----------
    map_target_rule
        Mapping from target ids to Rules.
    target
        The target to be updated.

    Returns
    -------
    graph
        Mapping from target ids to dependency target ids. Only such targets will
        be included that need to be updated to update the given target. The
        graph will be empty if there's nothing to update.
    """

    def build_graph(rule: Rule) -> dict[str, set[str]]:
        """Recursively build the target dependency graph."""
        graph: dict[str, set[str]] = dict()
        predecessors: set[str] = set()

        if isinstance(rule.target, Phony):
            target_timestamp = None
        else:
            target_timestamp = rule.target.timestamp
        # Rule is outdated because it has a Phony target or its target doesn't
        # exist.
        rule_is_outdated = target_timestamp is None

        if rule.deps:
            for dep in rule.deps:
                if callable(dep):
                    # Rule is outdated because its function dependency returns True.
                    rule_is_outdated |= dep()
                else:
                    if dep.id in map_target_rule:
                        dep_rule = map_target_rule[dep.id]

                        dep_graph = build_graph(dep_rule)
                        dep_is_outdated = bool(dep_graph)

                        if dep_is_outdated:
                            predecessors.add(dep_rule.target.id)
                            graph.update(dep_graph)

                        # Rule is outdated because its rule dependency is outdated.
                        rule_is_outdated |= dep_is_outdated

                        dep = dep_rule.target
                    elif isinstance(dep, Phony):
                        raise TypeError(
                            f"Phony target '{dep}' of no rule used as a dependency."
                        )
                    elif dep.timestamp is None:
                        raise RuntimeError(
                            f"Nonexistent dependency '{dep}' is not the target "
                            f"of any rule."
                        )

                    if target_timestamp is not None and hasattr(dep, "timestamp"):
                        dep_timestamp = dep.timestamp
                        if dep_timestamp is not None:
                            # Rule is outdated because its target is older than its
                            # dependency.
                            rule_is_outdated |= dep_timestamp > target_timestamp

        if rule_is_outdated:
            node = rule.target.id
            graph[node] = predecessors

        return graph

    return build_graph(map_target_rule[target.id])
