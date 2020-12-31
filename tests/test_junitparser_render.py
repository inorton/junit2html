"""
Test that we can load all our input files without error
"""
import pytest
from . import inputfiles
from junit2htmlreport import render, parserimpl


@pytest.mark.parametrize("filename", inputfiles.get_reports())
def test_load(filename):
    report = parserimpl.load_report(inputfiles.get_filepath(filename))
    assert report is not None

    doc = render.HTMLReport()
    doc.load(report, filename)

    output = str(doc)
    assert output
