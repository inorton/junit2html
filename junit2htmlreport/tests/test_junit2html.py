"""
Test that does nothing other than import
"""
import os
from junit2htmlreport.tests.inputfiles import get_filepath
from junit2htmlreport import runner


def test_runner(tmpdir):
    """
    Test the stand-alone app with a simple fairly empty junit file
    :param tmpdir:  py.test tmpdir fixture
    :return:
    """
    testfile = get_filepath("junit-simple_suites.xml")
    outfile = os.path.join(tmpdir.strpath, "report.html")
    runner.run([testfile, outfile])
    assert os.path.exists(outfile)
