"""
Handle multiple parsed junit reports
"""
from __future__ import unicode_literals
import os
from . import parser
from .common import ReportContainer
from .parser import SKIPPED, FAILED, PASSED, ABSENT
from .render import HTMLMatrix, HTMLReport

UNTESTED = "untested"
PARTIAL_PASS = "partial pass"
PARTIAL_FAIL = "partial failure"
TOTAL_FAIL = "total failure"


class ReportMatrix(ReportContainer):
    """
    Load and handle several report files
    """

    def __init__(self):
        super(ReportMatrix, self).__init__()
        self.cases = {}
        self.classes = {}
        self.casenames = {}
        self.result_stats = {}
        self.case_results = {}

    def add_case_result(self, case):
        testclass = case.testclass.name
        casename = case.name
        if testclass not in self.case_results:
            self.case_results[testclass] = {}
        if casename not in self.case_results[testclass]:
            self.case_results[testclass][casename] = []
        self.case_results[testclass][casename].append(case.outcome())

    def report_order(self):
        return sorted(self.reports.keys())

    def short_outcome(self, outcome):
        if outcome == PASSED:
            return "/"
        elif outcome == SKIPPED:
            return "s"
        elif outcome == FAILED:
            return "f"
        elif outcome == TOTAL_FAIL:
            return "F"
        elif outcome == PARTIAL_PASS:
            return "%"
        elif outcome == PARTIAL_FAIL:
            return "X"
        elif outcome == UNTESTED:
            return "U"

        return "?"

    def add_report(self, filename):
        """
        Load a report into the matrix
        :param filename:
        :return:
        """
        parsed = parser.Junit(filename=filename)
        filename = os.path.basename(filename)
        self.reports[filename] = parsed

        for suite in parsed.suites:
            for testclass in suite.classes:
                if testclass not in self.classes:
                    self.classes[testclass] = {}
                if testclass not in self.casenames:
                    self.casenames[testclass] = list()
                self.classes[testclass][filename] = suite.classes[testclass]

                for testcase in self.classes[testclass][filename].cases:
                    basename = testcase.basename().strip()
                    if basename not in self.casenames[testclass]:
                        self.casenames[testclass].append(basename)

                    if testclass not in self.cases:
                        self.cases[testclass] = {}
                    if basename not in self.cases[testclass]:
                        self.cases[testclass][basename] = {}
                    self.cases[testclass][basename][filename] = testcase

                    outcome = testcase.outcome()
                    self.add_case_result(testcase)

                    self.result_stats[outcome] = 1 + self.result_stats.get(
                        outcome, 0)

    def summary(self):
        """
        Render a summary of the matrix
        :return:
        """
        raise NotImplementedError()

    def combined_result(self, results):
        """
        Given a list of results, produce a "combined" overall result
        :param results:
        :return:
        """
        if PASSED in results:
            if FAILED in results:
                return self.short_outcome(PARTIAL_FAIL), PARTIAL_FAIL.title()
            return self.short_outcome(PASSED), PASSED.title()

        if FAILED in results:
            return self.short_outcome(FAILED), FAILED.title()
        if SKIPPED in results:
            return self.short_outcome(UNTESTED), UNTESTED.title()
        return " ", ""


class HtmlReportMatrix(ReportMatrix):
    """
    Render a matrix report as html
    """

    def __init__(self, outdir):
        super(HtmlReportMatrix, self).__init__()
        self.outdir = outdir

    def add_report(self, filename):
        """
        Load a report
        """
        super(HtmlReportMatrix, self).add_report(filename)
        basename = os.path.basename(filename)
        # make the individual report too
        report = self.reports[basename].html()
        if self.outdir != "" and not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        with open(
                os.path.join(self.outdir, basename) + ".html", "wb") as filehandle:
            filehandle.write(report.encode("utf-8"))

    def short_outcome(self, outcome):
        if outcome == PASSED:
            return "ok"
        return super(HtmlReportMatrix, self).short_outcome(outcome)

    def short_axis(self, axis):
        if axis.endswith(".xml"):
            return axis[:-4]
        return axis

    def summary(self):
        """
        Render the html
        :return:
        """
        html_matrix = HTMLMatrix(self)

        return str(html_matrix)


class TextReportMatrix(ReportMatrix):
    """
    Render a matrix report as text
    """

    def summary(self):
        """
        Render as a string
        :return:
        """

        output = "\nMatrix Test Report\n"
        output += "===================\n"

        axis = list(self.reports.keys())
        axis.sort()

        # find the longest classname or test case name
        left_indent = 0
        for classname in self.classes:
            left_indent = max(len(classname), left_indent)
            for casename in self.casenames[classname]:
                left_indent = max(len(casename), left_indent)

        # render the axis headings in a stepped tree
        treelines = ""
        for filename in self.report_order():
            output += "{}    {}{}\n".format(" " * left_indent, treelines,
                                            filename)
            treelines += "| "
        output += "{}    {}\n".format(" " * left_indent, treelines)
        # render in groups of the same class

        for classname in self.classes:
            # new class
            output += "{}  \n".format(classname)

            # print the case name
            for casename in sorted(set(self.casenames[classname])):
                output += "- {}{}  ".format(casename,
                                            " " * (left_indent - len(casename)))

                # print each test and its result for each axis
                case_data = ""
                for axis in self.report_order():
                    if axis not in self.cases[classname][casename]:
                        case_data += "  "
                    else:
                        testcase = self.cases[classname][casename][axis]
                        if testcase.skipped:
                            case_data += "s "
                        elif testcase.failure:
                            case_data += "f "
                        else:
                            case_data += "/ "

                combined, combined_name = self.combined_result(
                    self.case_results[classname][testcase.name])

                output += case_data
                output += " {} {}\n".format(combined, combined_name)

        # print the result stats

        output += "\n"
        output += "-" * 79
        output += "\n"

        output += "Test Results:\n"

        for outcome in sorted(self.result_stats):
            output += "  {:<12} : {:>6}\n".format(
                outcome.title(),
                self.result_stats[outcome])

        return output
