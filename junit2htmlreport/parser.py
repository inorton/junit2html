"""
Parse a junit report file into a family of objects
"""
from __future__ import unicode_literals
import xml.etree.ElementTree as ET
import collections
from junit2htmlreport import tag
from junit2htmlreport.textutils import unicode_str
import os
import uuid


NO_CLASSNAME = "no-testclass"

FAILED = "failed"  # the test failed
SKIPPED = "skipped"  # the test was skipped
PASSED = "passed"  # the test completed successfully
ABSENT = "absent"  # the test was known but not run/failed/skipped


class ParserError(Exception):
    """
    We had a problem parsing a file
    """
    def __init__(self, message):
        super(ParserError, self).__init__(message)


class HtmlHeadMixin(object):
    """
    Head a html page
    """
    def get_css(self):
        """
        Return the content of the css file
        :return:
        """
        thisdir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(thisdir, "report.css"), "r") as cssfile:
            return cssfile.read()

    def get_html_head(self, reportname):
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
        </head>""".format(css=self.get_css(), name=reportname)


class ToJunitXmlBase(object):
    """
    Base class of all objects that can be serialized to Junit XML
    """
    def tojunit(self):
        """
        Return an Element matching this object
        :return:
        """
        raise NotImplementedError()

    def make_element(self, xmltag, text=None, attribs=None):
        """
        Create an Element and put text and/or attribs into it
        :param xmltag: tag name
        :param text:
        :param attribs: dict of xml attributes
        :return:
        """
        element = ET.Element(unicode_str(xmltag))
        if text is not None:
            element.text = unicode_str(text)
        if attribs is not None:
            for item in attribs:
                element.set(unicode_str(item), unicode_str(attribs[item]))
        return element


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


class Property(AnchorBase, ToJunitXmlBase):
    """
    Test Properties
    """
    def _init_(self):
        super(Property, self).__init__()
        self.name = None
        self.value = None

    def tojunit(self):
        """
        Return the xml element for this property
        :return:
        """
        prop = self.make_element("property")
        prop.set(u"name", unicode_str(self.name))
        prop.set(u"value", unicode_str(self.value))
        return prop

    def html(self):
        """
       Render those properties as html
       :return:
       """
        return """
        <div class="property"><i>{name}</i><br/>
        <pre>{value}</pre></div>
        """.format(name=tag.text(self.name), value=tag.text(self.value))


class Case(AnchorBase, ToJunitXmlBase):
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

    def outcome(self):
        """
        Return the result of this test case
        :return:
        """
        if self.skipped:
            return SKIPPED
        elif self.failed():
            return FAILED
        return PASSED

    def tojunit(self):
        """
        Turn this test case back into junit xml
        :note: this may not be the exact input we loaded
        :return:
        """
        testcase = self.make_element("testcase")
        testcase.set(u"name", unicode_str(self.name))
        testcase.set(u"classname", unicode_str(self.testclass.name))
        testcase.set(u"time", unicode_str(self.duration))

        if self.stderr is not None:
            testcase.append(self.make_element("system-err", self.stderr))
        if self.stdout is not None:
            testcase.append(self.make_element("system-out", self.stdout))

        if self.failure is not None:
            testcase.append(self.make_element(
                "failure", self.failure,
                {
                    "message": self.failure_msg
                }))

        if self.skipped:
            testcase.append(self.make_element(
                "skipped", self.skipped,
                {
                    "message": self.skipped_msg
                }))

        if self.properties:
            props = self.make_element("properties")
            for prop in self.properties:
                props.append(prop.tojunit())
            testcase.append(props)

        return testcase

    def fullname(self):
        """
        Get the full name of a test case
        :return:
        """
        return "{} : {}".format(self.testclass.name, self.name)

    def basename(self):
        """
        Get a short name for this case
        :return:
        """
        if self.name.startswith(self.testclass.name):
            return self.name[len(self.testclass.name):]
        return self.name

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
        skipped = ""
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

        def render_stdoe():
            if self.stderr or self.stdout:
                return """
            <div class="stdout"><i>Stdout</i><br/>
                <pre>{stdout}</pre></div>
            <hr size="1"/>
            <div class="stderr"><i>Stderr</i><br/>
                <pre>{stderr}</pre></div>
                """.format(stderr=stderr, stdout=stdout)
            return ""

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
            {stdoe}
        </div>
    </a>
        """.format(anchor=self.anchor(),
                   testname=self.name,
                   testclassname=self.testclass.name,
                   duration=self.duration,
                   failure=failure,
                   skipped=skipped,
                   properties="".join(properties),
                   stdoe=render_stdoe())


class Suite(AnchorBase, ToJunitXmlBase):
    """
    Contains test cases (usually only one suite per report)
    """
    def __init__(self):
        super(Suite, self).__init__()
        self.name = None
        self.duration = 0
        self.classes = collections.OrderedDict()
        self.package = None
        self.properties = []
        self.errors = []
        self.stdout = None
        self.stderr = None

    def tojunit(self):
        """
        Return an element for this whole suite and all it's cases
        :return:
        """
        suite = self.make_element("testsuite")
        suite.set(u"name", unicode_str(self.name))
        suite.set(u"time", unicode_str(self.duration))
        if self.properties:
            props = self.make_element("properties")
            for prop in self.properties:
                props.append(prop.tojunit())
            suite.append(props)

        for testcase in self.all():
            suite.append(testcase.tojunit())
        return suite

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
        return [test for test in self.all() if not test.failed() and not test.skipped()]

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
                                   failure.testclass.name + '.' + failure.name)))

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

        package = ""
        if self.package is not None:
            package = "Package: " + self.package + "<br/>"

        for classname in self.classes:
            classes.append(self.classes[classname].html())

        errs = ""
        for error in self.errors:
            if not len(errs):
                errs += "<tr><th colspan='2' align='left'>Errors</th></tr>"
            for part in ["type", "message", "text"]:
                if part in error:
                    errs += "<tr><td>{}</td><td><pre>{}</pre></td></tr>".format(
                        part,
                        tag.text(error[part]))

        stdio = ""
        if self.stderr or self.stdout:
            stdio += "<tr><th colspan='2' align='left'>Output</th></tr>"
            if self.stderr:
                stdio += "<tr><td>Stderr</td><td><pre>{}</pre></td></tr>".format(
                        tag.text(self.stderr))
            if self.stdout:
                stdio += "<tr><td>Stdout</td><td><pre>{}</pre></td></tr>".format(
                        tag.text(self.stdout))

        props = ""
        if len(self.properties):
            props += "<table>"
            for prop in self.properties:
                # we dont call the html method, we want these in a table
                props += "<tr><th>{}</th><td>{}</td></tr>".format(
                    tag.text(prop.name), tag.text(prop.value))
            props += "</table>"

        return """
        <div class="testsuite">
            <h2>Test Suite: {name}</h2><a name="{anchor}">
            {package}
            {properties}
            <table>
            <tr><th align="left">Duration</th><td align="right">{duration} sec</td></tr>
            <tr><th align="left">Test Cases</th><td align="right">{count}</td></tr>
            <tr><th align="left">Failures</th><td align="right">{fails}</td></tr>
            {errs}
            {stdio}
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
                   anchor=self.anchor(),
                   duration=self.duration,
                   errs=errs,
                   stdio=stdio,
                   toc=self.toc(),
                   package=package,
                   properties=props,
                   classes="".join(classes),
                   count=len(self.all()),
                   fails=len(self.failed()))


class Junit(HtmlHeadMixin):
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

    def get_html_head(self, reportname):
        """
        Make the file header
        :param reportname:
        :return:
        """
        return super(Junit, self).get_html_head(reportname)

    def _read(self, xmlstring):
        """
        Populate the junit xml document tree from a string
        :param xmlstring:
        :return:
        """
        self.tree = ET.fromstring(xmlstring)

    def process(self):
        """
        populate the report from the xml
        :return:
        """
        suites = None
        if isinstance(self.tree, ET.ElementTree):
            root = self.tree.getroot()
        else:
            root = self.tree

        if root.tag == "testrun":
            root = root[0]

        if root.tag == "testsuite":
            suites = [root]

        if root.tag == "testsuites":
            suites = [x for x in root]

        if suites is None:
            raise ParserError("could not find test suites in results xml")
        suitecount = 0
        for suite in suites:
            suitecount += 1
            cursuite = Suite()
            self.suites.append(cursuite)
            suitename = suite.attrib.get("name", "suite-" + str(suitecount))
            cursuite.name = suitename
            if "package" in suite.attrib:
                cursuite.package = suite.attrib["package"]
            cursuite.duration = float(suite.attrib.get("time", '0').replace(',',''))

            for element in suite:
                if element.tag == "error":
                    # top level error?
                    errtag = {
                        "message": element.attrib.get("message", ""),
                        "type": element.attrib.get("type", ""),
                        "text": element.text
                    }
                    cursuite.errors.append(errtag)
                if element.tag == "system-out":
                    cursuite.stdout = element.text
                if element.tag == "system-err":
                    cursuite.stderr = element.text

                if element.tag == "properties":
                    for prop in element:
                        if prop.tag == "property":
                            newproperty = Property()
                            newproperty.name = prop.attrib["name"]
                            newproperty.value = prop.attrib["value"]
                            cursuite.properties.append(newproperty)

                if element.tag == "testcase":
                    testcase = element

                    if not testcase.attrib.get("classname", None):
                        testcase.attrib["classname"] = NO_CLASSNAME

                    if testcase.attrib["classname"] not in cursuite:
                        testclass = Class()
                        testclass.name = testcase.attrib["classname"]
                        cursuite[testclass.name] = testclass

                    testclass = cursuite[testcase.attrib["classname"]]
                    newcase = Case()
                    newcase.name = testcase.attrib["name"]
                    newcase.testclass = testclass
                    newcase.duration = float(testcase.attrib.get("time", '0').replace(',',''))
                    testclass.cases.append(newcase)

                    # does this test case have any children?
                    for child in testcase:
                        if child.tag == "skipped":
                            newcase.skipped = child.text
                            if "message" in child.attrib:
                                newcase.skipped_msg = child.attrib["message"]
                            if not newcase.skipped:
                               newcase.skipped = "skipped"
                        elif child.tag == "system-out":
                            newcase.stdout = child.text
                        elif child.tag == "system-err":
                            newcase.stderr = child.text
                        elif child.tag == "failure":
                            newcase.failure = child.text
                            if "message" in child.attrib:
                                newcase.failure_msg = child.attrib["message"]
                            if not newcase.failure:
                                newcase.failure = "failed"
                        elif child.tag == "error":
                            newcase.failure = child.text
                            if "message" in child.attrib:
                                newcase.failure_msg = child.attrib["message"]
                            if not newcase.failure:
                                newcase.failure = "error"
                        elif child.tag == "properties":
                            for property in child:
                                newproperty = Property()
                                newproperty.name = property.attrib["name"]
                                newproperty.value = property.attrib["value"]
                                newcase.properties.append(newproperty)

    def toc(self):
        """
        If this report has multiple suite results, make a table of contents listing each suite
        :return:
        """
        if len(self.suites) > 1:
            tochtml = "<ul>"
            for suite in self.suites:
                tochtml += '<li><a href="#{anchor}">{name}</a></li>'.format(
                        anchor=suite.anchor(),
                        name=tag.text(suite.name))
            tochtml += "</ul>"
            return tochtml
        else:
            return ""

    def html(self):
        """
        Render the test suite as a HTML report with links to errors first.
        :return:
        """

        page = self.get_html_head(self.filename)
        page += "<body><h1>Test Report</h1>"
        page += self.toc()
        for suite in self.suites:
            page += suite.html()
        page += "</body></html>"

        return page
