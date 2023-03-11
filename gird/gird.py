"""Main module with CLI."""

import argparse
import dataclasses
import os
import pathlib
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple, Union

from .common import (
    PARALLELISM_OFF,
    PARALLELISM_UNLIMITED_JOBS,
    MakefileConfig,
    Parallelism,
    Phony,
    Rule,
    RunConfig,
)
from .girdfile import import_girdfile
from .girdpath import get_gird_path_run, get_gird_path_tmp, init_gird_path
from .makefile import (
    format_target,
    get_question_file_path,
    get_target_name_for_question_rule,
    write_makefiles,
)


@dataclasses.dataclass
class ListConfig:
    """Configuration for the subcommand that lists all rules."""

    question: bool


def parse_args_and_init() -> Tuple[
    List[Rule],
    Union[RunConfig, ListConfig],
]:
    """Parse CLI arguments and do initialization.

    Initialization includes calling the functions init_gird_path,
    import_girdfile, & write_makefiles. It may not be done if the program exists
    in case of an error or based on CLI arguments.

    Returns
    -------
    rules
        Rules imported from a girdfile.
    config
        Configuration for further actions, depending on CLI arguments.
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

    def add_argument_help(parser):
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="Show this help message and exit.",
        )

    # Define --help here to be parsed after subparsers are completely defined.
    add_argument_help(group_options)

    girdfile_str = os.path.relpath(girdfile_to_import, current_dir)
    helptext_subparsers = "List all rules or run a single rule."
    if len(rules) > 0:
        targets_str = ", ".join(
            "'" + str(format_target(rule.target)) + "'" for rule in rules
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

    add_argument_help(parser_list)

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
            "-q",
            "--question",
            action="store_true",
            help=(
                '"Question mode".  Do not run any commands, or print anything; '
                "just return an exit status that is zero if the target is "
                "already up to date, nonzero otherwise."
            ),
        )

        add_argument_help(parser)

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

    args_rest = parser.parse_args(args_rest)
    subcommand = args_rest.subcommand

    if girdfile_import_error is not None:
        if girdfile_arg is not None or subcommand == subcommand_list:
            print_message(girdfile_import_error.args[0], use_stderr=True)
            sys.exit(1)

    if len(rules) == 0 or subcommand is None:
        parser.print_help()
        sys.exit(0)

    if subcommand != subcommand_list:
        if subcommand == subcommand_run:
            target = args_rest.target
        else:
            target = subcommand
        config = RunConfig(
            target=target,
            verbose=args_init.verbose or args_rest.dry_run,
            question=args_rest.question,
        )
        makefile_config = MakefileConfig(
            verbose=args_init.verbose or args_rest.dry_run,
            parallelism=args_rest.jobs,
            dry_run=args_rest.dry_run,
        )
    else:
        config = ListConfig(
            question=args_rest.question,
        )
        makefile_config = MakefileConfig(
            verbose=args_init.verbose,
            parallelism=PARALLELISM_OFF,
            dry_run=False,
        )

    write_makefiles(rules, makefile_config)

    return rules, config


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


def question_target(run_config: RunConfig) -> bool:
    """Get the state of a target with '--question'.

    Returns
    -------
    is_outdated
        True if the target is not up to date.
    """
    args = [
        "make",
        "--directory",
        str(get_gird_path_run().resolve()),
        "--file",
        str((get_gird_path_tmp() / "Makefile1").resolve()),
    ]
    if not run_config.verbose:
        args.append("--silent")
    target = run_config.target
    args.append(get_target_name_for_question_rule(target))
    process = subprocess.run(
        args,
        text=True,
    )
    exit_on_error(process, target)
    question_file = get_question_file_path(target)
    question_return_code = int(question_file.read_text().strip())
    is_outdated = question_return_code == 1
    return is_outdated


def run_rule(run_config: RunConfig):
    """Run a rule if its target is not up to date. Possibly exit the program.

    Parameters
    ----------
    run_config
        Run configuration.
    """
    is_outdated = question_target(run_config)
    target = run_config.target
    if run_config.question:
        sys.exit(int(is_outdated))
    elif not is_outdated:
        print_message(f"'{target}' is up to date.")
        sys.exit()

    args = [
        "make",
        "--directory",
        str(get_gird_path_run().resolve()),
        "--file",
        str((get_gird_path_tmp() / "Makefile1").resolve()),
    ]
    if not run_config.verbose:
        args.append("--silent")
    args.append(target)

    print_message(f"Executing rule of '{target}'.")

    process = subprocess.run(
        args,
        text=True,
    )

    exit_on_error(process, target)


def list_rules(
    rules: Iterable[Rule],
    list_config: ListConfig,
):
    """List all rules. Possibly exit the program."""
    parts = []
    for rule in rules:
        target_formatted = str(format_target(rule.target))

        if list_config.question:
            is_outdated = question_target(
                RunConfig(
                    target=target_formatted,
                    verbose=False,
                    question=False,
                )
            )

            if is_outdated and not isinstance(rule.target, Phony):
                indent_target = "* "
            else:
                indent_target = "  "
            indent_help = "      "
        else:
            indent_target = ""
            indent_help = "    "

        parts.append(indent_target + target_formatted)

        if rule.help:
            parts.append(
                "\n".join(indent_help + line for line in rule.help.split("\n"))
            )
    print("\n".join(parts))


def main():
    rules, config = parse_args_and_init()
    if isinstance(config, RunConfig):
        run_rule(config)
    else:
        list_rules(rules, config)
