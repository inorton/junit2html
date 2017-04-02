"""
Test that does nothing other than import
"""
import os
from inputfiles import get_filepath
from junit2htmlreport import runner, parser


def run_runner(tmpdir, filename):
    """
    Run the junit2html program against the given report and produce a html doc
    :param tmpdir:
    :param filename:
    :return:
    """
    testfile = get_filepath(filename=filename)
    outfile = os.path.join(tmpdir.strpath, "report.html")
    runner.run([testfile, outfile])
    assert os.path.exists(outfile)


def test_runner_simple(tmpdir):
    """
    Test the stand-alone app with a simple fairly empty junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    run_runner(tmpdir, "junit-simple_suites.xml")


def test_runner_complex(tmpdir):
    """
    Test the stand-alone app with a large fairly complex junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    run_runner(tmpdir, "junit-complex_suites.xml")


def test_runner_unicode(tmpdir):
    """
    Test the stand-alone app with a unicode file (contains a euro symbol)
    :param tmpdir:
    :return:
    """
    run_runner(tmpdir, "junit-unicode.xml")


def test_parser():
    """
    Test the junit parser directly
    :return:
    """
    junit = parser.Junit(filename=get_filepath("junit-simple_suite.xml"))
    assert len(junit.suites) == 1
    assert len(junit.suites[0].properties) == 3

    junit = parser.Junit(filename=get_filepath("junit-simple_suites.xml"))
    assert len(junit.suites) == 1
    assert len(junit.suites[0].properties) == 3

    junit = parser.Junit(filename=get_filepath("junit-complex_suites.xml"))
    assert len(junit.suites) == 66

    junit = parser.Junit(filename=get_filepath("junit-cute2.xml"))
    assert len(junit.suites) == 6

    junit = parser.Junit(filename=get_filepath("junit-unicode.xml"))
    assert len(junit.suites) == 1
    assert len(junit.suites[0].classes) == 1


def test_parser_stringreader():
    """
    Test the junit parser when reading strings
    :return:
    """
    with open(get_filepath("junit-complex_suites.xml"), "r") as data:
        junit = parser.Junit(xmlstring=data.read())
        assert len(junit.suites) == 66
        assert junit.suites[0].name == "Untitled suite in /Users/niko/Sites/casperjs/tests/suites/casper/agent.js"
        assert junit.suites[0].package == "tests/suites/casper/agent"
        assert junit.suites[0].classes["tests/suites/casper/agent"].cases[1].name == "Default user agent matches /plop/"
