# -*- coding: utf-8 -*-
from junit2htmlreport import runner
from .inputfiles import get_filepath


def test_matrix_stdout(capsys):
    runner.run(["--summary-matrix", get_filepath("junit-unicode.xml")])

    out, err = capsys.readouterr()

    assert u"A Class with a cent ¢" in out
    assert u"Euro € Test Case" in out