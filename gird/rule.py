"""The rule function."""
import pathlib
from typing import Iterable, Optional, Union

from .common import Dependency, Rule, SubRecipe, Target
from .girdfile import GIRDFILE_CONTEXT
from .object import Phony, TimeTrackedPath, is_timetracked

# Type aliases for the rule function API
ApiTarget = Union[pathlib.Path, Target]
ApiDependency = Union[pathlib.Path, Rule, Dependency]


def rule(
    target: ApiTarget,
    deps: Optional[
        Union[
            ApiDependency,
            Iterable[ApiDependency],
        ]
    ] = None,
    recipe: Optional[
        Union[
            SubRecipe,
            Iterable[SubRecipe],
        ]
    ] = None,
    help: Optional[str] = None,
    parallel: bool = True,
    listed: bool = True,
) -> Rule:
    """Define & register a Rule.

    Parameters
    ----------
    target
        Target of the rule.
    deps
        Dependencies of the target.
    recipe
        Recipe to update the target. Strings will be executed as shell commands.
        Python function recipes need to be picklable if parallel is True. I.e.,
        Lambda functions and locally defined functions require parallel to be
        False.
    help
        Helptext/description of the rule.
    parallel
        Run the rule in parallel with other rules, i.e., in a separate process.
        Recipes that require input may fail.
    listed
        Include the rule in `gird list`.

    Notes
    -----

    When invoked, a rule will be run if its target is considered outdated. This
    is the case if the rule
    1) has a `Phony` target,
    2) has a `Path` target that does not exist,
    3) has a `Path` target and a `Path` dependency that is more recent than the target,
    4) has an outdated `Rule`/target as a dependency, or
    5) has a function dependency that returns `True`.

    Rules with outdated targets are run in topological order within the
    dependency graph, i.e., all outdated dependencies are updated before the
    respective targets. By default, rules are run in parallel when possible.

    Examples
    --------

    A rule with files as its target & dependency. A girdfile.py with the
    following contents defines a single rule that, when `gird package.whl` is
    invoked, builds *package.whl* whenever *module.py* is modified. If module.py
    hasn't been modified, the packaging recipe will not be executed.

    >>> import pathlib
    >>> import gird
    >>>
    >>> RULE_BUILD = gird.rule(
    >>>     target=pathlib.Path("package.whl"),
    >>>     deps=pathlib.Path("module.py"),
    >>>     recipe="python -m build --wheel",
    >>> )

    A rule with a phony target. Phony targets can be used when there's not any
    actual target to update. The recipe of a rule with a phony target is always
    executed.

    >>> RULE_TEST = gird.rule(
    >>>     target=gird.Phony("test"),
    >>>     recipe="pytest",
    >>> )

    A rule with other rules as dependencies. This is equivalent to using the
    targets of the rules as dependencies. Here, a phony target is used to give
    an alias to a group of other rules.

    >>> gird.rule(
    >>>     target=gird.Phony("all"),
    >>>     deps=[
    >>>         RULE_TEST,
    >>>         RULE_BUILD,
    >>>     ],
    >>> )

    A compound recipe for mixing Python functions with shell commands.

    >>> FILE1 = pathlib.Path("file1")
    >>>
    >>> gird.rule(
    >>>     target=FILE1,
    >>>     recipe=[
    >>>         FILE1.touch,
    >>>         f"echo text >> {FILE1.resolve()}",
    >>>     ],
    >>> )

    A Python function as a recipe with parameters. Use, e.g.,
    `functools.partial` to turn a function and its arguments into a callable
    with no arguments.

    >>> import functools
    >>> import shutil
    >>>
    >>> FILE2 = pathlib.Path("file2")
    >>>
    >>> gird.rule(
    >>>     target=FILE2,
    >>>     deps=FILE1,
    >>>     recipe=functools.partial(shutil.copy, FILE1, FILE2),
    >>> )

    A Python function as a dependency to arbitrarily trigger rules. Below, have
    a remote file re-fetched if it has changed.

    >>> def has_remote_changed():
    >>>     return get_checksum_local() != get_checksum_remote()
    >>>
    >>> gird.rule(
    >>>     target=FILE1,
    >>>     deps=has_remote_changed,
    >>>     recipe=fetch_remote,
    >>> )

    Implement the `TimeTracked` protocol for custom targets & dependencies. Such
    types are treated identically to `Path` objects, which respectively have a
    time of modification that is tracked for resolving outdatedness.

    For example, define platform-specific logic to apply dependency tracking on
    a remote file.

    >>> class RemoteFile(gird.TimeTracked):
    >>>     def __init__(self, url: str):
    >>>         self._url = url
    >>>     @property
    >>>     def id(self):
    >>>         return self._url
    >>>     @property
    >>>     def timestamp(self):
    >>>         return get_remote_file_timestamp(self._url)
    >>>
    >>> gird.rule(
    >>>     target=FILE1,
    >>>     deps=RemoteFile(URL),
    >>>     recipe=fetch_remote,
    >>> )

    Define rules flexibly. All that matter are the `rule` function calls that
    are executed when the girdfile.py is imported. The structure of the file and
    other implementation details are completely up to the user.

    >>> RULES = [
    >>>     gird.rule(
    >>>         target=source.with_suffix(".gz"),
    >>>         deps=gird.rule(
    >>>             target=source,
    >>>             recipe=functools.partial(fetch_remote, source),
    >>>         ),
    >>>         recipe=f"gzip -k {source.resolve()}",
    >>>     )
    >>>     for source in [FILE1, FILE2]
    >>> ]
    """
    if isinstance(target, pathlib.Path):
        target = TimeTrackedPath(target)
    elif not is_timetracked(target) and not isinstance(target, Phony):
        raise TypeError(f"Invalid target type: '{target}'.")

    if deps is not None:
        if not isinstance(deps, Iterable):
            deps = [deps]

        deps_cast = []
        for dep in deps:
            if isinstance(dep, Rule):
                dep = dep.target
            if isinstance(dep, pathlib.Path):
                dep = TimeTrackedPath(dep)
            elif (
                not callable(dep)
                and not is_timetracked(dep)
                and not isinstance(dep, Phony)
            ):
                raise TypeError(f"Invalid deps type: '{dep}'.")
            deps_cast.append(dep)

        deps = tuple(deps_cast)

    if recipe is not None:
        if not isinstance(recipe, Iterable) or isinstance(recipe, str):
            recipe = (recipe,)

        # Ensure recipe is not a single-pass Iterator.
        recipe = tuple(recipe)

        for subrecipe in recipe:
            if not isinstance(subrecipe, str) and not callable(subrecipe):
                raise TypeError(f"Invalid recipe type: '{subrecipe}'.")

    rule_instance = Rule(
        target=target,
        deps=deps,
        recipe=recipe,
        help=help,
        parallel=parallel,
        listed=listed,
    )

    if GIRDFILE_CONTEXT.is_active():
        GIRDFILE_CONTEXT.add_rule(rule_instance)

    return rule_instance
