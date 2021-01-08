"""
Parse a junit report file into a family of objects
"""
from __future__ import unicode_literals

import os
import xml.etree.ElementTree as ET
import collections
from .textutils import unicode_str
from .render import HTMLReport
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

    def id(self):
        return self.anchor()

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


class Property(AnchorBase, ToJunitXmlBase):
    """
    Test Properties
    """
    def __init__(self):
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

    def prefix(self):
        if self.skipped:
            return "[S]"
        if self.failed():
            return "[F]"
        return ""

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

    def __iter__(self):
        return self.suites.__iter__()

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
        testrun = False
        suites = None
        if isinstance(self.tree, ET.ElementTree):
            root = self.tree.getroot()
        else:
            root = self.tree

        if root.tag == "testrun":
            testrun = True
            root = root[0]

        if root.tag == "testsuite":
            suites = [root]

        if root.tag == "testsuites" or testrun:
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
            cursuite.duration = float(suite.attrib.get("time", '0').replace(',', '') or '0')

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
                    newcase.duration = float(testcase.attrib.get("time", '0').replace(',','') or '0')
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

    def html(self):
        """
        Render the test suite as a HTML report with links to errors first.
        :return:
        """

        doc = HTMLReport()
        doc.load(self, os.path.basename(self.filename))
        return str(doc)
