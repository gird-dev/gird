"""Main module with CLI."""

import argparse
import pathlib
import subprocess
from typing import Iterable

from .common import Rule
from .girdfile import import_girdfile
from .girdpath import get_gird_path_run, get_gird_path_tmp, init_gird_path
from .makefile import write_makefiles


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
        "--girdpath",
        type=pathlib.Path,
        default=current_dir / ".gird",
        help="Path of the working directory for Gird. Defaults to ./.gird.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
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
    capture_output: bool = True,
):
    makefile_dir = get_gird_path_tmp()
    gird_path_run = get_gird_path_run()

    args = [
        "make",
        target,
        "-C",
        str(gird_path_run.resolve()),
        "-f",
        str((makefile_dir / "Makefile1").resolve()),
    ]

    process = subprocess.run(
        args,
        text=True,
        capture_output=capture_output,
    )

    if process.returncode != 0:
        command = " ".join(args)
        message = f"Command `{command}` returned exit code {process.returncode}."
        if process.stderr or process.stdout:
            message += "\n"
        if process.stderr:
            message += f"Stderr:\n{process.stderr}"
        if process.stdout:
            message += f"Stdout:\n{process.stdout}"
        raise RuntimeError(message)


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
    init_gird_path(args.girdpath, args.girdfile)
    rules = import_girdfile(args.girdfile)
    if args.list:
        list_rules(rules)
    write_makefiles(rules)
    if args.target:
        run_target(
            args.target,
            capture_output=not args.verbose,
        )
