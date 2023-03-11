import os
import pathlib
import shutil

from gird.girdfile import import_girdfile
from gird.rulesorter import RuleSorter
from gird.run import run_rules

TEST_DIR = pathlib.Path(__file__).parent


def test_graph(tmp_path):
    """Miscellaneous test for testing how RuleSorter & run_rules work with
    slightly more nested dependencies.
    """
    os.chdir(tmp_path)

    path_girdfile_original = TEST_DIR / "girdfile.py"
    path_girdfile = tmp_path / f"girdfile_{TEST_DIR.name}.py"
    shutil.copy(path_girdfile_original, path_girdfile)

    source1 = tmp_path / "source1"
    target3 = tmp_path / "target3"
    target4 = tmp_path / "target4"
    target5 = tmp_path / "target5"

    source1.write_text("source1")
    target4.write_text("line3")

    rules = import_girdfile(girdfile_path=path_girdfile)
    rule_sorter = RuleSorter(rules, target5)
    run_rules(rule_sorter)

    assert target3.exists()
