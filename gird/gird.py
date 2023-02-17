"""Main module with CLI."""

import argparse
import pathlib
import subprocess
from typing import Iterable

from .common import Rule
from .girddir import get_girddir_tmp, init_girddir
from .girdfile import import_girdfile
from .makefile import write_makefiles
from .utils import convert_cli_target_for_make


def parse_args() -> argparse.Namespace:
    current_dir = pathlib.Path.cwd()

    parser = argparse.ArgumentParser(
        description="Gird - A Make-like build tool & task runner",
    )
    parser.add_argument(
        "--girdfile",
        type=pathlib.Path,
        default=current_dir / "girdfile.py",
        help="Path to the file with rule definitions. Defaults to ./girdfile.py.",
    )
    parser.add_argument(
        "--girddir",
        type=pathlib.Path,
        default=current_dir / ".gird",
        help="Path of the working directory for Gird. Defaults to ./.gird.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Increase verbosity.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List targets.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target to be run. If not given, only process the rule definition file.",
    )

    args = parser.parse_args()
    return args


def run_target(
    target: str,
    rules: Iterable[Rule],
    capture_output: bool = True,
):
    makefile_dir = get_girddir_tmp()
    target = convert_cli_target_for_make(target, rules)
    subprocess.run(
        [
            "make",
            target,
            "-C",
            str(makefile_dir.resolve()),
            "-f",
            str((makefile_dir / "Makefile1").resolve()),
        ],
        check=True,
        capture_output=capture_output,
    )


def list_rules(rules: Iterable[Rule]):
    print("Targets:", flush=True)
    for rule in rules:
        print(f"    {rule.target}", flush=True)
        if rule.help:
            print(
                "\n".join("        " + line for line in rule.help.split("\n")),
                flush=True,
            )


def main():
    args = parse_args()
    init_girddir(args.girddir)
    rules = import_girdfile(args.girdfile)
    if args.list:
        list_rules(rules)
    write_makefiles(rules)
    if args.target:
        run_target(
            args.target,
            rules,
            capture_output=not args.verbose,
        )
