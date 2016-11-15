"""
Test that does nothing other than import
"""
import os
from junit2htmlreport.tests.inputfiles import get_filepath
from junit2htmlreport import runner, parser


def test_runner_simple(tmpdir):
    """
    Test the stand-alone app with a simple fairly empty junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    testfile = get_filepath("junit-simple_suites.xml")
    outfile = os.path.join(tmpdir.strpath, "report.html")
    runner.run([testfile, outfile])
    assert os.path.exists(outfile)


def test_runner_complex(tmpdir):
    """
    Test the stand-alone app with a large fairly complex junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    testfile = get_filepath("junit-complex_suites.xml")
    outfile = os.path.join(tmpdir.strpath, "report.html")
    runner.run([testfile, outfile])
    assert os.path.exists(outfile)


def test_parser():
    """
    Test the junit parser directly
    :return:
    """
    junit = parser.Junit(filename=get_filepath("junit-simple_suite.xml"))
    assert len(junit.suites) == 1

    junit = parser.Junit(filename=get_filepath("junit-simple_suites.xml"))
    assert len(junit.suites) == 1

    junit = parser.Junit(filename=get_filepath("junit-complex_suites.xml"))
    assert len(junit.suites) == 66
