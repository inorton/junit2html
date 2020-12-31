from xml.etree import ElementTree

from junit2htmlreport import parser as j2h


def test_public_api():
    container = j2h.Junit(xmlstring="""<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="suite"></testsuite>
    """)
    container.filename = "test_results.xml"
    document = j2h.Suite()
    container.suites = [document]
    document.name = "test report"
    document.duration = 0.1
    document.package = "com.tests"
    first = j2h.Class()
    first.name = "myclass"
    document.classes[first.name] = first

    test1 = j2h.Case()
    test1.name = "test_one"
    test1.duration = 1.1
    test1.testclass = first
    first.cases.append(test1)

    test2 = j2h.Case()
    test2.name = "test_two"
    test2.duration = 1.2
    test2.testclass = first
    first.cases.append(test2)

    skipped1 = j2h.Case()
    skipped1.name = "test_skippy"
    skipped1.duration = 1.3
    skipped1.testclass = first
    skipped1.skipped = "test skipped"
    skipped1.skipped_msg = "test was skipped at runtime"
    first.cases.append(skipped1)

    failed1 = j2h.Case()
    failed1.name = "test_bad"
    failed1.duration = 1.4
    failed1.testclass = first
    failed1.failure = "test failed"
    failed1.failure_msg = "an exception happened"
    first.cases.append(failed1)

    html = container.html()

    assert html
    assert "<html>" in html
    assert """<span class="testname"><b>test_skippy</b></span><br/>""" in html
    assert """<div class="failure"><b>Failed: an exception happened</b><br/>""" in html
