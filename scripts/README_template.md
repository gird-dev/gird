{{ note }}

# Gird

Gird is a lightweight & general-purpose [Make][make]-like build tool & task
runner for Python.

[make]: https://en.wikipedia.org/wiki/Make_(software)

### Example use cases

- Data science & data analytics workflows.
- Portable CI tasks.
- Less rule-heavy application build setups. (Build times may become noticeable
  with thousands of rules.)
- Any project where tasks need to be executed automatically when some
  dependencies are updated.

### Features

- A simple, expressive, and intuitive rule definition and execution scheme very
  close to that of Make.
- Configuration in Python, allowing straightforward and familiar usage, without
  the need for a dedicated rule definition syntax.
- Ability to take advantage of Python's flexibility and possibility to easily
  integrate with Python libraries and tools.
- Emphasis on API simplicity & ease of use.

## Installation

Install Gird from PyPI with `pip install gird`, or from sources with
`pip install .`.

Gird requires Python version 3.9 or newer, and is supported on Linux & macOS.

## Usage

Define "rules" in *girdfile.py*. Depending on the composition of a rule
definition, a rule can, for example,

- define a recipe to run a task, e.g., to update a target file,
- define prerequisites for the target, such as dependency files or other rules,
  and
- use Python functions for more complex dependency & recipe functionality.

A rule is invoked by `gird {target}`. To list rules, run `gird list`.

### Example girdfile.py

This is the girdfile.py of the project itself.

{{ example_girdfile }}

Respective output from `gird list`:

{{ example_gird_list }}

### Example rules

{{ example_rules }}
