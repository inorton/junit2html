"""
Tests for emitting junit xml
"""

from junit2htmlreport import parser, merge


def test_case_tojunit_failed():
    """
    Test coverting a failed case to xml
    :return:
    """
    testclass = parser.Class()
    testclass.name = "myclass"
    testcase = parser.Case()
    testcase.name = "mytest"
    testcase.testclass = testclass
    testcase.failure = "bad"
    testcase.failure_msg = "failed message"

    result = testcase.tojunit()
    assert len(result.getchildren()) == 1
    assert result.getchildren()[0].tag == "failure"
    assert result.getchildren()[0].text == "bad"
    assert result.getchildren()[0].get("message") == "failed message"


def test_case_tojunit():
    """
    Test converting a test case to a junit xml element
    :return:
    """
    testclass = parser.Class()
    testclass.name = "myclass"
    testcase = parser.Case()
    testcase.name = "mytest"
    testcase.testclass = testclass
    testcase.duration = 3.0
    testcase.stdout = "hello\nworld"
    testcase.stderr = "byee"
    testcase.skipped = "ignored"
    testcase.skipped_msg = "skipped message"

    result = testcase.tojunit()
    assert result.tag == "testcase"
    assert result.get("time") == "3.0"
    assert result.get("classname") == "myclass"
    assert result.get("name") == "mytest"

    assert len(result.getchildren()) == 3
    assert result.getchildren()[0].tag == "system-err"
    assert result.getchildren()[0].text == "byee"
    assert result.getchildren()[1].tag == "system-out"
    assert result.getchildren()[1].text == "hello\nworld"
    assert result.getchildren()[2].tag == "skipped"
    assert result.getchildren()[2].get("message") == "skipped message"
    assert result.getchildren()[2].text == "ignored"


def test_merge():
    """
    Test merging suites
    :return:
    """
    # make two suites, with two classes with each three cases
    suites = []
    for y in range(2):
        suite = parser.Suite()
        suites.append(suite)

        for x in range(2):
            testclass = parser.Class()
            testclass.name = "class.name{}_{}".format(y, x)
            suite.classes[testclass.name] = testclass
            for z in range(3):
                testcase = parser.Case()
                testcase.name = "testcase{}_{}_{}".format(y, x, z)
                testcase.testclass = testclass
                testclass.cases.append(testcase)
    merger = merge.Merger()
    for suite in suites:
        merger.add_suite(suite)

    result = merger.tojunit()
    assert result is not None

    output = merger.toxmlstring()
    assert output
