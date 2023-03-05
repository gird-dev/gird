"""Main module with CLI."""

import argparse
import os
import pathlib
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple

from .common import PARALLELISM_OFF, PARALLELISM_UNLIMITED_JOBS, Parallelism, Rule
from .girdfile import import_girdfile
from .girdpath import get_gird_path_run, get_gird_path_tmp, init_gird_path
from .makefile import format_target, write_makefiles

# Name of the subcommand that lists all rules.
SUBCOMMAND_LIST = "list"


def parse_args_import_rules() -> Tuple[
    List[Rule],
    str,
    Optional[Parallelism],
]:
    """Parse CLI arguments and import Rules from a girdfile. Call sys.exit() in
    case of an error or based on CLI arguments.

    Returns
    -------
    rules
        Rules imported from a girdfile.
    subcommand
        The name of the subcommand to be run. Either SUBCOMMAND_LIST or
        the name of a rule to be run.
    parallelism
        The selected parallelism state. Will be None if subcommand is
        SUBCOMMAND_LIST.
    """
    current_dir = pathlib.Path.cwd()

    parser = argparse.ArgumentParser(
        description="Gird - A Make-like build tool & task runner",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_options = parser.add_argument_group(title="options")

    group_options.add_argument(
        "-f",
        "--girdfile",
        type=pathlib.Path,
        default=None,
        help="Path to the file with rule definitions. Defaults to ./girdfile.py.",
    )

    group_options.add_argument(
        "-p",
        "--girdpath",
        type=pathlib.Path,
        default=current_dir / ".gird",
        help="Path of the working directory for Gird. Defaults to ./.gird.",
    )

    group_options.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase verbosity.",
    )

    args_init, args_rest = parser.parse_known_args()

    girdfile_arg: Optional[pathlib.Path] = args_init.girdfile
    girdfile_to_import: pathlib.Path = girdfile_arg or current_dir / "girdfile.py"

    # Initialize & import Rules from girdfile.
    init_gird_path(args_init.girdpath, girdfile_to_import)
    try:
        rules = import_girdfile(girdfile_to_import)
        girdfile_import_error = None
    except ImportError as e:
        girdfile_import_error = ImportError(*e.args)
        rules = []

    helptext_help = "Show this help message and exit."

    # Define --help here to be parsed after subparsers are completely defined.
    group_options.add_argument(
        "-h",
        "--help",
        action="help",
        help=helptext_help,
    )

    if len(rules) > 0:
        rules_str = (
            f" Rules defined in {os.path.relpath(girdfile_to_import, current_dir)} are: "
            + ", ".join("'" + str(format_target(rule.target)) + "'" for rule in rules)
            + "."
        )
    else:
        rules_str = ""

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        metavar=f"{{{SUBCOMMAND_LIST}, rule}}",
        help=(
            "List all rules or run a single rule. For rule-specific help, run "
            f"'gird [options] {{rule}} --help'.{rules_str}"
        ),
    )

    subparsers.add_parser(SUBCOMMAND_LIST, add_help=False)

    for rule in rules:
        subparser_rule = subparsers.add_parser(
            str(format_target(rule.target)),
            description=rule.help,
            add_help=False,
        )

        subparser_rule.add_argument(
            "-j",
            "--jobs",
            type=Parallelism,
            nargs="?",
            default=PARALLELISM_OFF,
            const=PARALLELISM_UNLIMITED_JOBS,
            help=(
                "Number of jobs for parallel execution (off by default). If no "
                "integer argument is given, set no limit for the number of "
                "parallel jobs. Output will be buffered per each target, if "
                "the used Make implementation supports the feature. (E.g., "
                "colored output may be turned off by some programs.) Recipes "
                "that require input may fail due to temporary input stream "
                "invalidation."
            ),
        )
        subparser_rule.add_argument(
            "-h",
            "--help",
            action="help",
            help=helptext_help,
        )

    args_rest = parser.parse_args(args_rest)
    subcommand = args_rest.subcommand

    if subcommand is not None and subcommand != SUBCOMMAND_LIST:
        parallelism = args_rest.jobs
    else:
        parallelism = None

    if girdfile_import_error is not None:
        if girdfile_arg is not None or subcommand == SUBCOMMAND_LIST:
            print_message(girdfile_import_error.args[0], use_stderr=True)
            sys.exit(1)

    if len(rules) == 0 or subcommand is None:
        parser.print_help()
        sys.exit(0)

    return rules, subcommand, parallelism


def print_message(message: str, use_stderr: bool = False):
    """Print message about, e.g., rule's execution progress. If use_stderr=True,
    use sys.stderr instead of sys.stdout.
    """
    file = sys.stderr if use_stderr else sys.stdout
    message_parts = ["gird:"]
    if use_stderr:
        message_parts.append("Error:")
    message_parts.append(message)
    print(" ".join(message_parts), file=file, flush=True)


def run_rule(
    rules: Iterable[Rule],
    rule: str,
    parallelism: Parallelism,
):
    """Run a rule. Call sys.exit(returncode) in case of non-zero return code.

    Parameters
    ----------
    rules
        Rules defined by a girdfile.
    rule
        The rule to run.
    parallelism
        Parallelism state.
    """
    write_makefiles(rules, parallelism)

    gird_path_tmp = get_gird_path_tmp()
    gird_path_run = get_gird_path_run()

    args = [
        "make",
        rule,
        "-C",
        str(gird_path_run.resolve()),
        "-f",
        str((gird_path_tmp / "Makefile1").resolve()),
    ]

    print_message(f"Executing rule '{rule}'.")

    process = subprocess.run(
        args,
        text=True,
    )

    if process.returncode != 0:
        print_message(
            (
                f"Execution of rule '{rule}' returned with error. Possible "
                f"output & error messages should be visible above."
            ),
            use_stderr=True,
        )
        sys.exit(process.returncode)
    else:
        print_message(f"Target '{rule}' was successfully executed.")


def list_rules(rules: Iterable[Rule]):
    parts = []
    for rule in rules:
        parts.append(str(rule.target))
        if rule.help:
            parts.append("\n".join("    " + line for line in rule.help.split("\n")))
    print("\n".join(parts))


def main():
    rules, subcommand, parallelism = parse_args_import_rules()
    if subcommand == SUBCOMMAND_LIST:
        list_rules(rules)
    else:
        run_rule(rules, subcommand, parallelism)
