"""Main module with CLI."""

import argparse
import os
import pathlib
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple

from .common import (
    PARALLELISM_OFF,
    PARALLELISM_UNLIMITED_JOBS,
    Parallelism,
    Rule,
    RunConfig,
)
from .girdfile import import_girdfile
from .girdpath import (
    get_gird_path_question,
    get_gird_path_run,
    get_gird_path_tmp,
    init_gird_path,
)
from .makefile import format_target, get_target_name_for_question_rule, write_makefiles

# Name of the subcommand that lists all rules.
SUBCOMMAND_LIST = "list"
SUBCOMMAND_RUN = "run"


def parse_args_import_rules() -> Tuple[
    List[Rule],
    str,
    Optional[RunConfig],
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
    run_config
        Run configuration. Will be None if subcommand is SUBCOMMAND_LIST.
    """
    current_dir = pathlib.Path.cwd()

    parser = argparse.ArgumentParser(
        description="Gird - A Make-like build tool & task runner",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
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

    girdfile_str = os.path.relpath(girdfile_to_import, current_dir)
    helptext_subparsers = "List all rules or run a single rule."
    if len(rules) > 0:
        targets_str = ", ".join(
            "'" + str(format_target(rule.target)) + "'" for rule in rules
        )
        helptext_subparsers += (
            f" Targets defined in {girdfile_str}: "
            + ", ".join("'" + str(format_target(rule.target)) + "'" for rule in rules)
            + "."
        )
        helptext_run = f"One of the rules defined in {girdfile_str}: {targets_str}."
    else:
        helptext_run = ""

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        metavar=f"{{{SUBCOMMAND_LIST}, [run] target}}",
        help=helptext_subparsers,
    )

    subparsers.add_parser(
        SUBCOMMAND_LIST,
        description=f"List all rules defined in {girdfile_str}.",
    )

    def add_run_parser_arguments(parser):
        """Add arguments for a parser with run functionality."""
        parser.add_argument(
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

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Print the commands that would be executed, but do not execute "
                "them. Sets also --verbose."
            ),
        )

        parser.add_argument(
            "--question",
            action="store_true",
            help=(
                '"Question mode".  Do not run any commands, or print anything; '
                "just return an exit status that is zero if the target is "
                "already up to date, nonzero otherwise."
            ),
        )

        parser.add_argument(
            "-h",
            "--help",
            action="help",
            help=helptext_help,
        )

    subparser_run = subparsers.add_parser(
        "run",
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

    args_rest = parser.parse_args(args_rest)
    subcommand = args_rest.subcommand

    if subcommand is not None and subcommand != SUBCOMMAND_LIST:
        if subcommand == SUBCOMMAND_RUN:
            target = args_rest.target
        else:
            target = subcommand
        run_config = RunConfig(
            target=target,
            verbose=args_init.verbose,
            parallelism=args_rest.jobs,
            dry_run=args_rest.dry_run,
            question=args_rest.question,
        )
    else:
        run_config = None

    if girdfile_import_error is not None:
        if girdfile_arg is not None or subcommand == SUBCOMMAND_LIST:
            print_message(girdfile_import_error.args[0], use_stderr=True)
            sys.exit(1)

    if len(rules) == 0 or subcommand is None:
        parser.print_help()
        sys.exit(0)

    return rules, subcommand, run_config


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


def exit_on_error(process: subprocess.CompletedProcess, target: str):
    """Print error & call sys.exit(returncode) in case the return code of a
    process is non-zero.
    """
    if process.returncode != 0:
        print_message(
            (
                f"Execution of rule of '{target}' returned with error. Possible "
                f"output & error messages should be visible above."
            ),
            use_stderr=True,
        )
        sys.exit(process.returncode)


def run_rule(
    rules: Iterable[Rule],
    run_config: RunConfig,
):
    """Run a rule. Call exit_on_error after each subprocess.

    Parameters
    ----------
    rules
        Rules defined by a girdfile.
    run_config
        Run configuration.
    """
    write_makefiles(rules, run_config)

    gird_path_tmp = get_gird_path_tmp()
    gird_path_run = get_gird_path_run()

    args_common = [
        "make",
        "--directory",
        str(gird_path_run.resolve()),
        "--file",
        str((gird_path_tmp / "Makefile1").resolve()),
    ]

    if not run_config.verbose:
        args_common.append("--silent")

    target = run_config.target
    args_question = args_common + [get_target_name_for_question_rule(target)]
    args_run = args_common + [target]

    process = subprocess.run(
        args_question,
        text=True,
    )

    exit_on_error(process, target)

    question_file = get_gird_path_question() / target
    question_return_code = int(question_file.read_text().strip())
    if question_return_code == 0:
        if not run_config.question:
            print_message(f"'{target}' is up to date.")
        sys.exit()
    elif run_config.question:
        sys.exit(question_return_code)

    print_message(f"Executing rule of '{target}'.")

    process = subprocess.run(
        args_run,
        text=True,
    )

    exit_on_error(process, target)


def list_rules(rules: Iterable[Rule]):
    parts = []
    for rule in rules:
        parts.append(str(rule.target))
        if rule.help:
            parts.append("\n".join("    " + line for line in rule.help.split("\n")))
    print("\n".join(parts))


def main():
    rules, subcommand, run_config = parse_args_import_rules()
    if subcommand == SUBCOMMAND_LIST:
        list_rules(rules)
    else:
        run_rule(rules, run_config)
