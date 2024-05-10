"""
Test the matrix functionality
"""
import os

from junit2htmlreport import matrix
from junit2htmlreport.parser import CaseResult

from .inputfiles import HERE, get_filepath


def test_combined_result():
    """
    Test that the combined result string and short result value are correct
    :return:
    """
    textmatrix = matrix.TextReportMatrix()
    short, result = textmatrix.combined_result([CaseResult.PASSED, CaseResult.SKIPPED])

    assert short == textmatrix.short_outcome(CaseResult.PASSED)
    assert result == CaseResult.PASSED.title()

    short, result = textmatrix.combined_result([CaseResult.PASSED, CaseResult.FAILED])
    assert short == textmatrix.short_outcome(CaseResult.PARTIAL_FAIL)
    assert result == CaseResult.PARTIAL_FAIL.title()

    short, result = textmatrix.combined_result([CaseResult.PARTIAL_PASS])
    assert short == textmatrix.short_outcome(CaseResult.PARTIAL_PASS)
    assert result == CaseResult.PARTIAL_PASS.title()

    short, result = textmatrix.combined_result([CaseResult.TOTAL_FAIL])
    assert short == textmatrix.short_outcome(CaseResult.TOTAL_FAIL)
    assert result == CaseResult.TOTAL_FAIL.title()

    short, result = textmatrix.combined_result([CaseResult.FAILED, CaseResult.FAILED])
    assert short == textmatrix.short_outcome(CaseResult.FAILED)
    assert result == CaseResult.FAILED.title()

    short, result = textmatrix.combined_result([CaseResult.PASSED])
    assert short == textmatrix.short_outcome(CaseResult.PASSED)
    assert result == CaseResult.PASSED.title()

    short, result = textmatrix.combined_result([CaseResult.SKIPPED, CaseResult.SKIPPED])
    assert short == textmatrix.short_outcome(CaseResult.UNTESTED)
    assert result == CaseResult.UNTESTED.title()

    short, result = textmatrix.combined_result([])
    assert '?' == textmatrix.short_outcome(None) # type: ignore
    assert result == CaseResult.UNKNOWN.title()


def test_matrix_load(tmpdir):
    """
    Test loading multiple reports
    :return:
    """
    textmatrix = matrix.TextReportMatrix()
    textmatrix.add_report(get_filepath("junit-simple_suite.xml"))
    textmatrix.add_report(get_filepath("junit-simple_suites.xml"))
    textmatrix.add_report(get_filepath("junit-unicode.xml"))
    textmatrix.add_report(get_filepath("junit-unicode2.xml"))
    textmatrix.add_report(get_filepath("junit-cute2.xml"))
    textmatrix.add_report(get_filepath("junit-jenkins-stdout.xml"))

    assert len(textmatrix.reports) == 6

    result = textmatrix.summary()

    print(result)


def test_matrix_html(tmpdir):
    """
    Test loading multiple reports
    :return:
    """
    htmatrix = matrix.HtmlReportMatrix(str(tmpdir))
    htmatrix.add_report(get_filepath("junit-simple_suite.xml"))
    htmatrix.add_report(get_filepath("junit-simple_suites.xml"))
    htmatrix.add_report(get_filepath("junit-unicode.xml"))
    htmatrix.add_report(get_filepath("junit-axis-linux.xml"))
    assert len(htmatrix.reports) == 4
    result = htmatrix.summary()
    assert result.endswith("</html>")

