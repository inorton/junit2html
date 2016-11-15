"""
Parse a junit report file into a family of objects
"""

import xml.etree.ElementTree as ET
import collections
from junit2htmlreport import tag
import os
import uuid


class AnchorBase(object):
    """
    Base class that can generate a unique anchor name.
    """
    def __init__(self):
        self._anchor = None

    def anchor(self):
        """
        Generate a html anchor name
        :return:
        """
        if not self._anchor:
            self._anchor = str(uuid.uuid4())
        return self._anchor


class Class(AnchorBase):
    """
    A namespace for a test
    """
    def __init__(self):
        super(Class, self).__init__()
        self.name = None
        self.cases = list()

    def html(self):
        """
        Render this test class as html
        :return:
        """
        cases = [x.html() for x in self.cases]

        return """
        <hr size="2"/>
        <a name="{anchor}">
        <div class="testclass">
            <div>Test Class: {name}</div>
            <div class="testcases">
            {cases}
            </div>
        </div>
        </a>
        """.format(anchor=self.anchor(),
                   name=tag.text(self.name),
                   count=len(cases),
                   cases="".join(cases))

class Property(AnchorBase):
    """
    Test Properties
    """
    def _init_(self):
        super(Property, self).__init__()
        self.name=None
        self.value=None

    def html(self):
        """
       Render those properties as html
       :return:
       """
        return """
        <div class="property"><i>{name}</i><br/>
        <pre>{value}</pre></div>
        """.format(name=tag.text(self.name), value=tag.text(self.value))

class Case(AnchorBase):
    """
    Test cases
    """
    def __init__(self):
        super(Case, self).__init__()
        self.failure = None
        self.failure_msg = None
        self.skipped = False
        self.skipped_msg = None
        self.stderr = None
        self.stdout = None
        self.duration = 0
        self.name = None
        self.testclass = None
        self.properties = list()

    def failed(self):
        """
        Return True if this test failed
        :return:
        """
        return self.failure is not None

    def html(self):
        """
        Render this test case as HTML
        :return:
        """
        failure = ""
        skipped = None
        stdout = tag.text(self.stdout)
        stderr = tag.text(self.stderr)

        if self.skipped:
            skipped = """
            <hr size="1"/>
            <div class="skipped"><b>Skipped: {msg}</b><br/>
                <pre>{skip}</pre>
            </div>
            """.format(msg=tag.text(self.skipped_msg),
                       skip=tag.text(self.skipped))

        if self.failed():
            failure = """
            <hr size="1"/>
            <div class="failure"><b>Failed: {msg}</b><br/>
                <pre>{fail}</pre>
            </div>
            """.format(msg=tag.text(self.failure_msg),
                       fail=tag.text(self.failure))

        properties = [x.html() for x in self.properties]

        return """
    <a name="{anchor}">
        <div class="testcase">
            <div class="details">
                <span class="testname"><b>{testname}</b></span><br/>
                <span class="testclassname">{testclassname}</span><br/>
                <span class="duration">Time Taken: {duration}s</span>
            </div>
            {skipped}
            {failure}
            <hr size="1"/>
            {properties}
            <div class="stdout"><i>Stdout</i><br/>
                <pre>{stdout}</pre></div>
            <hr size="1"/>
            <div class="stderr"><i>Stderr</i><br/>
                <pre>{stderr}</pre></div>
        </div>
    </a>
        """.format(anchor=self.anchor(),
                   testname=self.name,
                   testclassname=self.testclass.name,
                   duration=self.duration,
                   failure=failure,
                   skipped=skipped,
                   properties="".join(properties),
                   stdout=stdout,
                   stderr=stderr)


class Suite(object):
    """
    Contains test cases (usually only one suite per report)
    """
    def __init__(self):
        self.name = None
        self.duration = 0
        self.classes = collections.OrderedDict()
        self.properties = {}

    def __contains__(self, item):
        """
        Return True if the given test classname is part of this test suite
        :param item:
        :return:
        """
        return item in self.classes

    def __getitem__(self, item):
        """
        Return the given test class object
        :param item:
        :return:
        """
        return self.classes[item]

    def __setitem__(self, key, value):
        """
        Add a test class
        :param key:
        :param value:
        :return:
        """
        self.classes[key] = value

    def all(self):
        """
        Return all testcases
        :return:
        """
        tests = list()
        for testclass in self.classes:
            tests.extend(self.classes[testclass].cases)
        return tests

    def failed(self):
        """
        Return all the failed testcases
        :return:
        """
        return [test for test in self.all() if test.failed()]

    def skipped(self):
        """
        Return all skipped testcases
        :return:
        """
        return [test for test in self.all() if test.skipped]

    def passed(self):
        """
        Return all the passing testcases
        :return:
        """
        return [test for test in self.all() if not test.failed()]

    def toc(self):
        """
        Return a html table of contents
        :return:
        """
        fails = ""
        skips = ""

        if len(self.failed()):
            faillist = list()
            for failure in self.failed():
                faillist.append(
                    """
                    <li>
                        <a href="#{anchor}">{name}</a>
                    </li>
                    """.format(anchor=failure.anchor(),
                               name=tag.text(
                                   failure.testclass.name + failure.name)))

            fails = """
            <li>Failures
            <ul>{faillist}</ul>
            </li>
            """.format(faillist="".join(faillist))

        if len(self.skipped()):
            skiplist = list()
            for skipped in self.skipped():
                skiplist.append(
                    """
                    <li>
                        <a href="#{anchor}">{name}</a>
                    </li>
                    """.format(anchor=skipped.anchor(),
                               name=tag.text(
                                   skipped.testclass.name + skipped.name)))

            skips = """
            <li>Skipped
            <ul>{skiplist}</ul>
            </li>
            """.format(skiplist="".join(skiplist))

        classlist = list()
        for classname in self.classes:
            testclass = self.classes[classname]

            cases = list()
            for testcase in testclass.cases:
                if "pkcs11" in testcase.name:
                    assert True

                cases.append(
                    """
                    <li>
                        <a href="#{anchor}">{name}</a>
                    </li>
                    """.format(anchor=testcase.anchor(),
                               name=tag.text(testcase.name)))

            classlist.append("""
            <li>
                <a href="#{anchor}">{name}</a>
                <ul>
                {cases}
                </ul>
            </li>
            """.format(anchor=testclass.anchor(),
                       name=testclass.name,
                       cases="".join(cases)))

        return """
        <ul>
            {failed}
            {skips}
            <li>All Test Classes
            <ul>{classlist}</ul>
            </li>
        </ul>
        """.format(failed=fails,
                   skips=skips,
                   classlist="".join(classlist))

    def html(self):
        """
        Render this as html.
        :return:
        """
        classes = list()

        for classname in self.classes:
            classes.append(self.classes[classname].html())

        props = ""
        if len(self.properties):
            props += "<table>"
            propnames = sorted(self.properties)
            for prop in propnames:
                props += "<tr><th>{}</th><td>{}</td></tr>".format(prop, self.properties[prop])
            props += "</table>"

        return """
        <div class="testsuite">
            <h2>Test Suite: {name}</h2>
            {properties}
            <table>
            <tr><th align="left">Duration</th><td align="right">{duration} sec</td></tr>
            <tr><th align="left">Test Cases</th><td align="right">{count}</td></tr>
            <tr><th align="left">Failures</th><td align="right">{fails}</td></tr>
            </table>
            <a name="toc"></a>
            <h2>Results Index</h2>
            {toc}
            <hr size="2"/>
            <h2>Test Results</h2>
            <div class="testclasses">
            {classes}
            </div>
        </div>
        """.format(name=tag.text(self.name),
                   duration=self.duration,
                   toc=self.toc(),
                   properties=props,
                   classes="".join(classes),
                   count=len(self.all()),
                   fails=len(self.failed()))


class Junit(object):
    """
    Parse a single junit xml report
    """

    def __init__(self, filename=None, xmlstring=None):
        """
        Parse the file
        :param filename:
        :return:
        """
        self.filename = filename
        self.tree = None
        if filename is not None:
            self.tree = ET.parse(filename)
        elif xmlstring is not None:
            self._read(xmlstring)
        else:
            raise ValueError("Missing any filename or xmlstring")
        self.suites = []
        self.process()
        self.css = "report.css"

    def _read(self, xmlstring):
        """
        Populate the junit xml document tree from a string
        :param xmlstring:
        :return:
        """
        self.tree = ET.fromstring(xmlstring)

    def get_css(self):
        """
        Return the content of the css file
        :return:
        """
        thisdir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(thisdir, self.css), "rb") as cssfile:
            return cssfile.read()

    def process(self):
        """
        populate the report from the xml
        :return:
        """
        root = self.tree.getroot()

        if root.tag == "testsuite":
            suites = [root]
        elif root.tag == "testsuites":
            suites = [x for x in root]

        for suite in suites:
            cursuite = Suite()
            self.suites.append(cursuite)
            cursuite.name = suite.attrib["name"]
            cursuite.duration = float(root.attrib.get("time", '0'))

            for testcase in suite:
                if testcase.tag == "testcase":
                    if testcase.attrib["classname"] not in cursuite:
                        testclass = Class()
                        testclass.name = testcase.attrib["classname"]
                        if not testclass.name:
                            testclass.name = "no-classname-set"

                        cursuite[testclass.name] = testclass

                    newcase = Case()
                    newcase.name = testcase.attrib["name"]
                    newcase.testclass = testclass
                    newcase.duration = float(testcase.attrib["time"])
                    testclass.cases.append(newcase)

                    # does this test case have any children?
                    for child in testcase:
                        if child.tag == "skipped":
                            newcase.skipped = child.text
                            if "message" in child.attrib:
                                newcase.skipped_msg = child.attrib["message"]
                        elif child.tag == "system-out":
                            newcase.stdout = child.text
                        elif child.tag == "system-err":
                            newcase.stderr = child.text
                        elif child.tag == "failure":
                            newcase.failure = child.text
                            if "message" in child.attrib:
                                newcase.failure_msg = child.attrib["message"]
                        elif child.tag == "error":
                            newcase.failure = child.text
                            if "message" in child.attrib:
                                newcase.failure_msg = child.attrib["message"]
                        elif child.tag == "properties":
                            for property in child:
                                newproperty = Property()
                                newproperty.name = property.attrib["name"]
                                newproperty.value = property.attrib["value"]
                                newcase.properties.append(newproperty)

    def get_html_head(self):
        """
        Get the HTML head
        :return:
        """
        return """
        <html>
        <head>
            <title>{name} - Junit Test Report</title>
            <style type="text/css">
              {css}
            </style>
        </head>""".format(css=self.get_css(), name=self.filename)

    def html(self):
        """
        Render the test suite as a HTML report with links to errors first.
        :return:
        """

        page = self.get_html_head()
        page += "<body><h1>Test Report</h1>"
        for suite in self.suites:
            page += suite.html()
        page += "</body></html>"

        return page
