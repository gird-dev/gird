"""Module for running Rules."""
import concurrent.futures
import io
import subprocess
import sys
from typing import Dict

from .common import Rule
from .rulesorter import RuleSorter


def run_rule(
    rule: Rule,
    dry_run: bool = False,
    output_sync: bool = False,
):
    """Run the recipe of a Rule.

    Parameters
    ----------
    rule
        The Rule to run.
    dry_run
        Print the commands and function calls that would be executed, but do not
        execute them.
    output_sync
        Print the output of the run all at once after the entire recipe has
        finished.
    """
    if rule.recipe is None:
        return

    stdout_original = sys.stdout
    if output_sync:
        sys.stdout = io.StringIO()

    for subrecipe in rule.recipe:
        if isinstance(subrecipe, str):
            if dry_run:
                print(subrecipe)
            else:
                process = subprocess.run(subrecipe, shell=True)
                if process.returncode > 0:
                    raise RuntimeError(
                        f"Command '{subrecipe}' exited with error code {process.returncode}."
                    )
        else:
            if dry_run:
                print(f"{subrecipe.__name__}()")
            else:
                subrecipe()

    if output_sync:
        output = sys.stdout.getvalue()
        sys.stdout = stdout_original
        print(output, end="")


def run_rules(
    sorter: RuleSorter,
    dry_run: bool = False,
    output_sync: bool = False,
):
    """Run Rules as sorted by a RuleSorter.

    The recipes of the Rules will be run either concurrently, using
    concurrent.futures.ProcessPoolExecutor, or in this process, depending on
    the 'parallel' field of the Rules.

    Parameters
    ----------
    sorter
        The RuleSorter to dictate the order in which the Rules ar run.
    dry_run
        See the function 'run_rule'.
    output_sync
        See the function 'run_rule'.
    """
    sorter.prepare()

    executor = concurrent.futures.ProcessPoolExecutor()
    map_future_target: Dict[concurrent.futures.Future, str] = dict()
    while sorter.is_active():
        targets = sorter.get_ready()
        targets_done = set()
        for target in targets:
            rule = sorter.map_target_rule[target]
            if rule.parallel:
                future = executor.submit(
                    run_rule,
                    rule,
                    dry_run=dry_run,
                    output_sync=output_sync,
                )
                map_future_target[future] = target
            else:
                run_rule(
                    rule,
                    dry_run=dry_run,
                    output_sync=output_sync,
                )
                targets_done.add(target)

        if not targets_done:
            completed_future = next(
                concurrent.futures.as_completed(map_future_target.keys())
            )
            target = map_future_target.pop(completed_future)
            exception = completed_future.exception()
            if exception:
                raise exception
            targets_done.add(target)

        for target in targets_done:
            sorter.done(target)
