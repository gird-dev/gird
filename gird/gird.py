"""Main module with CLI."""

import argparse
import dataclasses
import enum
import os
import pathlib
import sys
import traceback
from typing import Iterable, List, Optional, Tuple, Union

from .common import Phony, Rule, Target
from .girdfile import import_girdfile
from .rulesorter import RuleSorter, format_target
from .run import run_rules


@dataclasses.dataclass
class RunConfig:
    """Configuration for the subcommand for running rules."""

    target: Target
    verbose: bool = False
    question: bool = False
    dry_run: bool = False
    output_sync: bool = False


@dataclasses.dataclass
class ListConfig:
    """Configuration for the subcommand that lists all rules."""

    question: bool
    all: bool


class SubcommandResult(enum.Enum):
    """Result values of the run_rule & list functions."""

    OK = enum.auto()
    QUESTION_OUTDATED = enum.auto()
    QUESTION_UPTODATE = enum.auto()
    RUN_UNNECESSARY = enum.auto()


def print_message(message: str, use_stderr: bool = False):
    """Print message about, e.g., rule's execution progress. If use_stderr=True,
    use sys.stderr instead of sys.stdout.
    """
    file = sys.stderr if use_stderr else sys.stdout
    error_prefix = "Error: " if use_stderr else ""
    print(f"gird: {error_prefix}{message}", file=file, flush=True)


def exit_on_exception(exception: Exception):
    """Print error and exit program with error code."""
    tback = "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )
    print_message(
        f"{exception}\n\n{tback}",
        use_stderr=True,
    )
    sys.exit(1)


def exit_with_result(result: SubcommandResult):
    """Exit the program with an exit code based on SubcommandResult value."""
    if result == SubcommandResult.QUESTION_UPTODATE:
        exit(0)
    elif result == SubcommandResult.QUESTION_OUTDATED:
        exit(1)
    else:
        exit(0)


def parse_args_and_init() -> Tuple[
    List[Rule],
    Union[RunConfig, ListConfig],
]:
    """Parse CLI arguments, import rules from a girdfile, and change current
    working directory to the directory with the girdfile. Exit the program if no
    further processing is needed.

    Returns
    -------
    rules
        Rules imported from a girdfile.
    config
        Configuration for further actions, depending on CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Gird - A Make-like build tool & task runner",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        exit_on_error=False,
    )

    group_options = parser.add_argument_group(title="optional arguments")

    group_options.add_argument(
        "-f",
        "--girdfile",
        type=pathlib.Path,
        default=None,
        help="Path to the file with rule definitions. Defaults to ./girdfile.py.",
    )

    group_options.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase verbosity.",
    )

    group_options.add_argument(
        "--output-sync",
        action="store_true",
        help=(
            "When running rules in parallel, ensure the output of each rule is "
            "collected together rather than interspersed with output from "
            "other rules."
        ),
    )

    args_init, args_rest = parser.parse_known_args()

    cwd_original = pathlib.Path.cwd()
    girdfile_arg: Optional[pathlib.Path] = args_init.girdfile
    girdfile_to_import: pathlib.Path = cwd_original / (girdfile_arg or "girdfile.py")
    os.chdir(girdfile_to_import.parent)
    girdfile_str = os.path.relpath(girdfile_to_import, cwd_original)

    # Import Rules from girdfile.
    girdfile_import_error = None
    try:
        rules = import_girdfile(girdfile_to_import)
    except (ImportError, ValueError) as e:
        girdfile_import_error = ImportError(
            f"Could not import girdfile '{girdfile_str}'."
        )
        girdfile_import_error.__cause__ = e
        rules = []

    def add_argument_help(helpless_parser):
        helpless_parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="Show this help message and exit.",
        )

    # Define --help here to be parsed after subparsers are completely defined.
    add_argument_help(group_options)

    helptext_subparsers = "List all rules or run a single rule."
    if len(rules) > 0:
        targets_str = ", ".join(
            "'" + str(format_target(rule.target)) + "'" for rule in rules if rule.listed
        )
        helptext_subparsers += f" Targets defined in {girdfile_str}: {targets_str}."
        helptext_run = f"One of the targets defined in {girdfile_str}: {targets_str}."
    else:
        helptext_subparsers += " Currently none are defined."
        helptext_run = ""

    # Name of the subcommand that lists all rules.
    subcommand_list = "list"
    # Name of the subcommand that runs a rule.
    subcommand_run = "run"

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        metavar=f"{{{subcommand_list}, [{subcommand_run}] target}}",
        help=helptext_subparsers,
    )

    parser_list = subparsers.add_parser(
        subcommand_list,
        description=f"List all rules defined in {girdfile_str}.",
        add_help=False,
    )

    parser_list.add_argument(
        "-q",
        "--question",
        action="store_true",
        help=(
            "Mark with '*' the rules that have a non-phony target that is not "
            "up to date."
        ),
    )

    parser_list.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Include also rules defined with 'listed=False'.",
    )

    add_argument_help(parser_list)

    def add_run_parser_arguments(run_parser):
        """Add arguments for a parser with run functionality."""
        run_parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Print the commands and function calls that would be executed, "
                "but do not execute them."
            ),
        )

        run_parser.add_argument(
            "-q",
            "--question",
            action="store_true",
            help=(
                '"Question mode".  Do not run any commands, or print anything; '
                "just return an exit status that is zero if the target is "
                "already up to date, nonzero otherwise."
            ),
        )

        add_argument_help(run_parser)

    subparser_run = subparsers.add_parser(
        subcommand_run,
        description="Run the rule of a target.",
        add_help=False,
    )
    subparser_run.add_argument("target", help=helptext_run)
    add_run_parser_arguments(subparser_run)

    for rule in rules:
        subparser_rule = subparsers.add_parser(
            str(format_target(rule.target)),
            description=rule.help,
            add_help=False,
        )
        add_run_parser_arguments(subparser_rule)

    try:
        args_rest = parser.parse_args(args_rest)
    except argparse.ArgumentError as e:
        if girdfile_import_error is not None:
            raise girdfile_import_error
        else:
            raise e

    subcommand = args_rest.subcommand

    if girdfile_import_error is not None:
        if girdfile_arg is not None or subcommand == subcommand_list:
            raise girdfile_import_error

    if len(rules) == 0 or subcommand is None:
        parser.print_help()
        sys.exit(0)

    if subcommand != subcommand_list:
        if subcommand == subcommand_run:
            target = args_rest.target
        else:
            target = subcommand
        for rule in rules:
            if target == format_target(rule.target):
                target = rule.target
                break
        config = RunConfig(
            target=target,
            verbose=args_init.verbose,
            question=args_rest.question,
            dry_run=args_rest.dry_run,
            output_sync=args_init.output_sync,
        )
    else:
        config = ListConfig(
            question=args_rest.question,
            all=args_rest.all,
        )

    return rules, config


def run_rule(rules: Iterable[Rule], config: RunConfig) -> SubcommandResult:
    """Run a rule if its target is not up to date.

    Parameters
    ----------
    rules
        Rules defined in a girdfile.
    config
        Run configuration.
    """
    rule_sorter = RuleSorter(rules, config.target)

    is_target_outdated = rule_sorter.is_target_outdated()

    if config.question:
        if is_target_outdated:
            result = SubcommandResult.QUESTION_OUTDATED
        else:
            result = SubcommandResult.QUESTION_UPTODATE
    elif not is_target_outdated:
        print_message(f"'{config.target}' is up to date.")
        result = SubcommandResult.RUN_UNNECESSARY
    else:
        print_message(f"Executing rule '{config.target}'.")
        run_rules(
            rule_sorter,
            dry_run=config.dry_run,
            output_sync=config.output_sync,
        )
        result = SubcommandResult.OK

    return result


def list_rules(
    rules: Iterable[Rule],
    config: ListConfig,
) -> SubcommandResult:
    """List rules."""
    parts = []
    for rule in rules:
        if not rule.listed and not config.all:
            continue

        if config.question:
            rule_sorter = RuleSorter(rules, rule.target)

            if rule_sorter.is_target_outdated() and not isinstance(rule.target, Phony):
                indent_target = "* "
            else:
                indent_target = "  "
            indent_help = "      "
        else:
            indent_target = ""
            indent_help = "    "

        parts.append(indent_target + format_target(rule.target))

        if rule.help:
            parts.append(
                "\n".join(indent_help + line for line in rule.help.split("\n"))
            )
    print("\n".join(parts))

    return SubcommandResult.OK


def main():
    try:
        rules, config = parse_args_and_init()
    except Exception as e:
        exit_on_exception(e)
        raise

    if isinstance(config, RunConfig):
        func = run_rule
    else:
        func = list_rules

    try:
        result = func(rules, config)
    except Exception as e:
        exit_on_exception(e)
        raise

    exit_with_result(result)
