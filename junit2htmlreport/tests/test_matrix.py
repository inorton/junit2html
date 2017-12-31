"""
Test the matrix functionality
"""
from inputfiles import get_filepath
from junit2htmlreport import matrix


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

    assert len(htmatrix.reports) == 2

    result = htmatrix.summary()

    assert result.endswith("</html>")
