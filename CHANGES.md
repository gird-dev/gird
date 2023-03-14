## 2.0.0

### Breaking changes

- Increase Python requirement to 3.9 or newer.

### API

- Function dependencies don't need to be decorated.
- Parallelism can now be defined per each rule.
- Rules are now immutable and hashable.
- Possibility to exclude rule from 'gird list'.

### CLI

- New argument '--output-sync'.
- New argument '--all' for the 'list' subcommand to list also targets that
  are defined with 'listed=False'.
- New argument '--question' for the 'list' subcommand to add an asterisk in
  front of every non-phony target that is not up to date.
- Shorthand argument '-q' for '--question'.
- Removed argument '--girdpath' as there's no need for any directory anymore.

### Other

- Removed dependency on Make.