"""
Classes for merging several reports into one
"""
from __future__ import unicode_literals
from io import BytesIO
from junit2htmlreport import parser
from junit2htmlreport.textutils import unicode_str
import xml.etree.ElementTree as ET


class Merger(parser.ToJunitXmlBase):
    """
    Utility class to create a merged junix xml report
    """
    def __init__(self):
        self.suites = []

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
        tree = ET.ElementTree(self.tojunit())
        buf = BytesIO()
        tree.write(buf)
        return u'<?xml version="1.0" encoding="utf-8"?>' + u"\n" + unicode_str(buf.getvalue())
