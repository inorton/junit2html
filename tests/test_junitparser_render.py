"""
Test that the junitparser implimentation renders HTML correctly
"""
import pytest
from . import inputfiles
from junit2htmlreport import html, parserimpl


@pytest.mark.parametrize("filename", inputfiles.get_reports())
def test_load(filename):
    if "junit-testrun.xml" in filename:
        pytest.xfail("junitparser can't load <testrun> reports - https://github.com/weiwei/junitparser/issues/59")

    report = parserimpl.load_report(inputfiles.get_filepath(filename))
    assert report is not None
