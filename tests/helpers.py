"""
Helper funcs for tests
"""
import os
from .inputfiles import get_filepath
from junit2htmlreport import runner


def run_runner(tmpdir, filename, *extra):
    """
    Run the junit2html program against the given report and produce a html doc
    :param tmpdir:
    :param filename:
    :param extra: addtional arguments
    :return:
    """
    testfile = get_filepath(filename=filename)
    if not len(extra):
        outfile = os.path.join(tmpdir.strpath, "report.html")
        runner.run([testfile, outfile])
        assert os.path.exists(outfile)
    else:
        runner.run([testfile] + list(extra))


def test_runner_simple(tmpdir):
    """
    Test the stand-alone app with a simple fairly empty junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    run_runner(tmpdir, "junit-simple_suites.xml")
