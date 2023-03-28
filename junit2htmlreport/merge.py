"""
Classes for merging several reports into one
"""
from __future__ import unicode_literals
import os
from io import BytesIO
from junit2htmlreport import parser
from junit2htmlreport.common import ReportContainer
from junit2htmlreport.textutils import unicode_str
from lxml import etree


def has_xml_header(filepath):
    """
    Return True if the first line of the file is <?xml
    :param filepath:
    :return:
    """
    return True


class Merger(ReportContainer, parser.ToJunitXmlBase):
    """
    Utility class to create a merged junix xml report
    """
    def __init__(self):
        super(Merger, self).__init__()
        self.suites = []

    def add_report(self, filename):
        """
        Load a test report or folder
        :param filename:
        :return:
        """
        if os.path.isfile(filename):
            report = parser.Junit(filename)
            self.reports[filename] = report
            for suite in report.suites:
                self.suites.append(suite)
        elif os.path.isdir(filename):
            # try importing all files in this folder
            for root, dirs, files in os.walk(filename):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if has_xml_header(filepath):
                        try:
                            self.add_report(filepath)
                        except (parser.ParserError, ET.ParseError):
                            pass

    def add_suite(self, suite):
        """
        Add a suite to the merge
        :param suite:
        :return:
        """
        self.suites.append(suite)

    def calculate_duration(self):
        """
        Add up the time values in all testcases
        :return:
        """
        total = 0
        for suite in self.suites:
            for testcase in suite.all():
                total += testcase.duration
        return total

    def tojunit(self):
        """
        Render a merged xml report
        :return:
        """
        root = self.make_element("testsuites")
        root.set(u"duration", unicode_str(self.calculate_duration()))
        for suite in self.suites:
            root.append(suite.tojunit())
        return root

    def toxmlstring(self):
        """
        Render the xml document as a string
        :return:
        """
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(self.tojunit(), parser=parser)
        buf = BytesIO()
        tree.write(buf)
        return u'<?xml version="1.0" encoding="utf-8"?>' + u"\n" + unicode_str(buf.getvalue())
