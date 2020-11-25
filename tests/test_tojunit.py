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
    children = list(result)
    assert len(children) == 1
    assert children[0].tag == "failure"
    assert children[0].text == "bad"
    assert children[0].get("message") == "failed message"


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
    children = list(result)
    assert len(children) == 3
    assert children[0].tag == "system-err"
    assert children[0].text == "byee"
    assert children[1].tag == "system-out"
    assert children[1].text == "hello\nworld"
    assert children[2].tag == "skipped"
    assert children[2].get("message") == "skipped message"
    assert children[2].text == "ignored"


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
