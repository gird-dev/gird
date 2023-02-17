from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from gird import rule

README_TEMPLATE = Path(__file__).parent / "README_template.md"
README = Path(__file__).parents[1] / "README.md"

JINJA_ENV = Environment(
    loader=FileSystemLoader(README_TEMPLATE.parent), keep_trailing_newline=True
)


def get_readme_examples() -> str:
    """Format the example section for README.md based on the docstring of the
    gird.rule function.
    """
    rule_doc = rule.__doc__
    examples_raw = rule_doc.split("Examples\n    --------\n\n")[1]
    items_raw = examples_raw.split("\n\n")
    items_formatted = []
    for item_raw in items_raw:
        lines_raw = [line_raw.strip() for line_raw in item_raw.split("\n")]
        if lines_raw[0].startswith(">>>"):
            lines_formatted = [line_raw[4:] for line_raw in lines_raw]
            lines_formatted.insert(0, "```python")
            lines_formatted.append("```")
        else:
            lines_formatted = lines_raw
        item_formatted = "\n".join(lines_formatted)
        items_formatted.append(item_formatted)
    examples_formatted = "\n\n".join(items_formatted)
    return examples_formatted


def generate_readme():
    template = JINJA_ENV.get_template(README_TEMPLATE.name)

    examples = get_readme_examples()
    readme_contents = template.render(examples=examples)

    with open(README, "w") as readme_file:
        readme_file.write(readme_contents)


def main():
    generate_readme()


if __name__ == "__main__":
    main()
