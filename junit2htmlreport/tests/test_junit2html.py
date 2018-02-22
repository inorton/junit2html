"""
Test that does nothing other than import
"""
import os
from inputfiles import get_filepath
from helpers import run_runner
from junit2htmlreport import parser, runner


def test_runner_sonobouy(tmpdir):
    """
    Test the stand-alone app with report produced by sonobouy
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    run_runner(tmpdir, "junit-sonobouy.xml")


def test_runner_complex(tmpdir):
    """
    Test the stand-alone app with a large fairly complex junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    run_runner(tmpdir, "junit-complex_suites.xml")


def test_runner_6700(tmpdir):
    """
    Test the 6700 report
    I can't remember what is special about this file!
    :param tmpdir:
    :return:
    """
    run_runner(tmpdir, "junit-report-6700.xml")


def test_runner_unicode(tmpdir):
    """
    Test the stand-alone app with a unicode file (contains a euro symbol)
    :param tmpdir:
    :return:
    """
    run_runner(tmpdir, "junit-unicode.xml")


def test_runner_testrun(tmpdir):
    """
    Test the stand-alone app with a file rooted at <testrun>
    :param tmpdir:
    :return:
    """
    run_runner(tmpdir, "junit-testrun.xml")


def test_runner_merge(tmpdir):
    """
    Test merging multiple files
    :param tmpdir:
    :return:
    """
    filenames = ["junit-complex_suites.xml",
                 "junit-cute2.xml",
                 "junit-unicode.xml"]

    filepaths = []
    for filename in filenames:
        filepaths.append(
            os.path.join(tmpdir.strpath, get_filepath(filename)))
    newfile = os.path.join(tmpdir.strpath, "merged.xml")
    args = ["--merge", newfile]
    args.extend(filepaths)
    runner.run(args)
    assert os.path.exists(newfile)


def test_emit_stdio():
    """
    Test the stand-alone app can generate a page from a report containing stdio text
    But also save the result in the current folder
    :return:
    """
    folder = os.path.dirname(__file__)
    reportfile = os.path.join(folder, "junit-jenkins-stdout.xml")
    runner.run([reportfile])
    htmlfile = os.path.join(folder, "junit-jenkins-stdout.xml.html")
    assert os.path.exists(htmlfile)
    with open(htmlfile, "r") as readfile:
        content = readfile.read()
        assert "===&gt; Executing test case" in content


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

    # different report structure, both files contain unicode symbols
    junit = parser.Junit(filename=get_filepath("junit-unicode2.xml"))
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
