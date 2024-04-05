"""
Parse a junit report file into a family of objects
"""
from __future__ import unicode_literals

import os
import sys
import xml.etree.ElementTree as ET
import collections
import os
import uuid
import xml.etree.ElementTree as ET
from typing import Any, OrderedDict

from .case_result import CaseResult
from .render import HTMLReport
from .textutils import unicode_str

NO_CLASSNAME = "no-testclass"


def clean_xml_attribute(element: ET.Element, attribute: str, default: str|None=None):
    """
    Get an XML attribute value and ensure it is legal in XML
    :param element:
    :param attribute:
    :param default:
    :return:
    """

    value = element.attrib.get(attribute, default)
    if value:
        value = value.encode("utf-8", errors="replace").decode("utf-8", errors="backslashreplace")
        value = value.replace(u"\ufffd", "?")  # strip out the unicode replacement char

    return value


class ParserError(Exception):
    """
    We had a problem parsing a file
    """
    def __init__(self, message: str):
        super(ParserError, self).__init__(message)


class ToJunitXmlBase(object):
    """
    Base class of all objects that can be serialized to Junit XML
    """
    def tojunit(self) -> ET.Element:
        """
        Return an Element matching this object
        :return:
        """
        raise NotImplementedError()

    def make_element(self, xmltag: str, text: str|None=None, attribs: dict[str, Any]|None=None):
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
    name: str|None = None
    cases: "list[Case]"
    
    def __init__(self):
        super(Class, self).__init__()
        self.cases = []


class Property(AnchorBase, ToJunitXmlBase):
    """
    Test Properties
    """
    def __init__(self):
        super(Property, self).__init__()
        self.name: str|None = None
        self.value: str|None = None

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
    failure: str|None = None
    failure_msg: str|None = None
    skipped: str|None = None
    skipped_msg: str|None = None
    stderr: str|Any|None = None
    stdout: str|Any|None = None
    duration: float = 0
    name: str|None = None
    testclass: Class|None = None
    properties: list[Property]

    def __init__(self):
        super(Case, self).__init__()
        self.properties = []

    @property
    def display_suffix(self):
        if self.skipped:
            return "[s]"
        return ""

    def outcome(self) -> CaseResult:
        """
        Return the result of this test case
        :return:
        """
        if self.skipped:
            return CaseResult.SKIPPED
        elif self.failed():
            return CaseResult.FAILED
        return CaseResult.PASSED

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
        if self.testclass is None or self.testclass.name is None:
            testclass_name = ""
        else:
            testclass_name = self.testclass.name

        testcase = self.make_element("testcase")
        testcase.set(u"name", unicode_str(self.name))
        testcase.set(u"classname", unicode_str(testclass_name))
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
        if self.testclass is None or self.testclass.name is None:
            testclass_name = ""
        else:
            testclass_name = self.testclass.name
        return "{} : {}".format(testclass_name, self.name)

    def basename(self):
        """
        Get a short name for this case
        :return:
        """
        if (   self.name is None
            or self.testclass is None
            or self.testclass.name is None
        ):
            return None

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
    name: str|None = None
    properties: list[Property]
    classes: OrderedDict[str, Class]
    duration: float = 0
    package: str|None = None
    errors: list[dict[str, str|Any|None]]
    stdout: str|Any|None = None
    stderr: str|Any|None = None

    def __init__(self):
        super(Suite, self).__init__()
        self.classes = collections.OrderedDict()
        self.properties = []
        self.errors = []

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

    def __contains__(self, item: str):
        """
        Return True if the given test classname is part of this test suite
        :param item:
        :return:
        """
        return item in self.classes

    def __getitem__(self, item: str):
        """
        Return the given test class object
        :param item:
        :return:
        """
        return self.classes[item]

    def __setitem__(self, key: str, value: Class):
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
        tests: list[Case] = []
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
        return [test for test in self.all() if not test.failed() and not test.skipped]


class Junit(object):
    """
    Parse a single junit xml report
    """
    filename: str
    suites: list[Suite]
    tree: ET.ElementTree|ET.Element

    def __init__(self, filename: str|None=None, xmlstring: str|None=None):
        """
        Parse the file
        :param filename:
        :return:
        """
        self.filename = filename
        if filename == "-":
            # read the xml from stdin
            stdin = sys.stdin.read()
            xmlstring = stdin
            self.filename = None

        self.tree = None
        if self.filename is not None:
            self.tree = ET.parse(self.filename)

        self.suites = []
        if filename is not None:
            self.filename = filename
            self.tree = ET.parse(filename)
        elif xmlstring is not None:
            self.tree = ET.fromstring(xmlstring)
        else:
            raise ValueError("Missing any filename or xmlstring")
        self.process()

    def __iter__(self):
        return self.suites.__iter__()

    def process(self):
        """
        populate the report from the xml
        :return:
        """
        testrun = False
        suites: list[ET.Element]|None = None
        root: ET.Element
        if isinstance(self.tree, ET.ElementTree):
            root = self.tree.getroot()
        else:
            root = self.tree

        if root.tag == "testrun":
            testrun = True
            root: ET.Element = root[0]

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
            cursuite.name = clean_xml_attribute(suite, "name", default="suite-" + str(suitecount))
            cursuite.package = clean_xml_attribute(suite, "package")

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

                    testclass: Class = cursuite[testcase.attrib["classname"]]
                    newcase = Case()
                    newcase.name = clean_xml_attribute(testcase, "name")
                    newcase.testclass = testclass
                    newcase.duration = float(testcase.attrib.get("time", '0').replace(',', '') or '0')
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
        title = "Test Results"
        if self.filename:
            if os.path.exists(self.filename):
                title = os.path.basename(self.filename)
        doc.load(self, title=title)
        return str(doc)
