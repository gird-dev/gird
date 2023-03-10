import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from gird import rule

ROOT_PATH = Path(__file__).parents[1]
GIRDFILE = ROOT_PATH / "girdfile.py"
README_TEMPLATE = Path(__file__).parent / "README_template.md"
README = ROOT_PATH / "README.md"

JINJA_ENV = Environment(
    loader=FileSystemLoader(README_TEMPLATE.parent), keep_trailing_newline=True
)


def get_readme_example_girdfile() -> str:
    return f"```python\n{GIRDFILE.read_text().strip()}\n```"


def get_readme_example_gird_list() -> str:
    process = subprocess.run(["gird", "list"], text=True, stdout=subprocess.PIPE)
    return f"```\n{process.stdout}```"


def get_readme_example_rules() -> str:
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


def get_readme_contents() -> str:
    template = JINJA_ENV.get_template(README_TEMPLATE.name)
    example_girdfile = get_readme_example_girdfile()
    example_gird_list = get_readme_example_gird_list()
    example_rules = get_readme_example_rules()
    readme_contents = template.render(
        example_girdfile=example_girdfile,
        example_gird_list=example_gird_list,
        example_rules=example_rules,
    )
    return readme_contents


def assert_readme_updated():
    """Raise an AssertionError if the contents of the README file don't equal
    the text returned by get_readme_contents.
    """
    readme_contents = get_readme_contents()
    if README.read_text() != readme_contents:
        raise AssertionError("README.md is not updated.")


def render_readme():
    """Write the text returned by get_readme_contents to the README file."""
    readme_contents = get_readme_contents()
    with open(README, "w") as readme_file:
        readme_file.write(readme_contents)


def main():
    render_readme()


if __name__ == "__main__":
    main()
