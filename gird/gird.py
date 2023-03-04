"""Main module with CLI."""

import argparse
import pathlib
import subprocess
import sys
from typing import Iterable, List, Tuple

from .common import Rule
from .girdfile import import_girdfile
from .girdpath import get_gird_path_run, get_gird_path_tmp, init_gird_path
from .makefile import format_target, write_makefiles

# Name of the subcommand to list all rules.
SUBCOMMAND_LIST = "list"


def parse_args_import_rules() -> Tuple[List[Rule], str]:
    """Parse CLI arguments and import Rules from a girdfile. Call sys.exit() in
    case of an error or based on CLI arguments.

    Returns
    -------
    rules
        Rules imported from a girdfile.
    subcommand
        The name of the subcommand to be run. Either SUBCOMMAND_LIST or
        the name of a rule to be run.
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
        default=current_dir / "girdfile.py",
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

    # Initialize & import Rules from girdfile.
    init_gird_path(args_init.girdpath, args_init.girdfile)
    try:
        rules = import_girdfile(args_init.girdfile)
    except ImportError as e:
        print_message(e.args[0], stderr=True)
        sys.exit(1)

    # Define --help here to be parsed after subparsers are completely defined.
    group_options.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit.",
    )

    help_rules = "one of " + ", ".join(
        "'" + str(format_target(rule.target)) + "'" for rule in rules
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        metavar=f"{{{SUBCOMMAND_LIST}, rule}}",
        help=f"List all rules or run a single rule ({help_rules}).",
    )

    subparsers.add_parser(SUBCOMMAND_LIST, add_help=False)

    for rule in rules:
        subparsers.add_parser(str(format_target(rule.target)), add_help=False)

    args_rest = parser.parse_args(args_rest)
    subcommand = args_rest.subcommand

    if subcommand is None:
        parser.print_help()
        sys.exit(0)

    return rules, subcommand


def print_message(message: str, stderr: bool = False):
    """Print message about, e.g., rule's execution progress. If stderr=True,
    use sys.stderr instead of sys.stdout.
    """
    file = sys.stderr if stderr else sys.stdout
    print(f"gird: {message}", file=file, flush=True)


def run_rule(rules: Iterable[Rule], rule: str):
    """Run a rule. Call sys.exit(returncode) in case of non-zero return code."""
    write_makefiles(rules)

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
            stderr=True,
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
    rules, subcommand = parse_args_import_rules()
    if subcommand == SUBCOMMAND_LIST:
        list_rules(rules)
    else:
        run_rule(rules, subcommand)
