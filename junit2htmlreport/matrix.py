"""
Handle multiple parsed junit reports
"""
from __future__ import unicode_literals

import os
from typing import TYPE_CHECKING

from . import parser
from .case_result import CaseResult
from .common import ReportContainer
from .render import HTMLMatrix

UNTESTED = CaseResult.UNTESTED
PARTIAL_PASS = CaseResult.PARTIAL_PASS
PARTIAL_FAIL = CaseResult.PARTIAL_FAIL
TOTAL_FAIL = CaseResult.TOTAL_FAIL


if TYPE_CHECKING: # pragma: no cover
    from .parser import Case, Class
    from typing import Dict, List, Optional, Any, Literal


class ReportMatrix(ReportContainer):
    """
    Load and handle several report files
    """
    cases: "Dict[str, Dict[str, Dict[str, Case]]]"
    classes: "Dict[str, Dict[str, Class]]"
    casenames: "Dict[str, List[str]]"
    result_stats: "Dict[CaseResult, int]"
    case_results: "Dict[str, Dict[str, List[CaseResult]]]"

    def __init__(self):
        super(ReportMatrix, self).__init__()
        self.cases = {}
        self.classes = {}
        self.casenames = {}
        self.result_stats = {}
        self.case_results = {}

    def add_case_result(self, case: "Case"):
        if case.testclass is None or case.testclass.name is None:
            testclass = ""
        else:
            testclass = case.testclass.name
        casename = "" if case.name is None else case.name
        if testclass not in self.case_results:
            self.case_results[testclass] = {}
        if casename not in self.case_results[testclass]:
            self.case_results[testclass][casename] = []
        self.case_results[testclass][casename].append(case.outcome())

    def report_order(self):
        return sorted(self.reports.keys())

    def short_outcome(self, outcome: CaseResult) -> "Literal['ok', '/', 's', 'f', 'F', '%', 'X', 'U', '?']":
        if outcome == CaseResult.PASSED:
            return "/"
        elif outcome == CaseResult.SKIPPED: # pragma: no cover
            return "s" # currently unused because SKIPPED returns UNTESTED
        elif outcome == CaseResult.FAILED:
            return "f"
        elif outcome == CaseResult.TOTAL_FAIL:
            return "F"
        elif outcome == CaseResult.PARTIAL_PASS:
            return "%"
        elif outcome == CaseResult.PARTIAL_FAIL:
            return "X"
        elif outcome == CaseResult.UNTESTED:
            return "U"

        return "?"

    def add_report(self, filename: str):
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
                    name = "" if testcase.name is None else testcase.name.strip()
                    if name not in self.casenames[testclass]:
                        self.casenames[testclass].append(name)

                    if testclass not in self.cases:
                        self.cases[testclass] = {}
                    if name not in self.cases[testclass]:
                        self.cases[testclass][name] = {}
                    self.cases[testclass][name][filename] = testcase

                    outcome = testcase.outcome()
                    self.add_case_result(testcase)

                    self.result_stats[outcome] = 1 + self.result_stats.get(
                        outcome, 0)

    def summary(self) -> str:
        """
        Render a summary of the matrix
        :return:
        """
        raise NotImplementedError()

    def combined_result_list(self, classname: str, casename: str):
        """
        Combone the result of all instances of the given case
        :param classname:
        :param casename:
        :return:
        """
        if classname in self.case_results:
            if casename in self.case_results[classname]:
                results = self.case_results[classname][casename]
                return self.combined_result(results)

        return " ", ""

    def combined_result(self, results: "List[CaseResult]"):
        """
        Given a list of results, produce a "combined" overall result
        :param results:
        :return:
        """
        if results:
            if CaseResult.PASSED in results:
                if CaseResult.FAILED in results:
                    return self.short_outcome(CaseResult.PARTIAL_FAIL), CaseResult.PARTIAL_FAIL.title()
                return self.short_outcome(CaseResult.PASSED), CaseResult.PASSED.title()

            if CaseResult.FAILED in results:
                return self.short_outcome(CaseResult.FAILED), CaseResult.FAILED.title()
            if CaseResult.SKIPPED in results:
                return self.short_outcome(CaseResult.UNTESTED), CaseResult.UNTESTED.title()
            if CaseResult.PARTIAL_PASS in results:
                return self.short_outcome(CaseResult.PARTIAL_PASS), CaseResult.PARTIAL_PASS.title()
            if CaseResult.TOTAL_FAIL in results:
                return self.short_outcome(CaseResult.TOTAL_FAIL), CaseResult.TOTAL_FAIL.title()
        return " ", ""


class HtmlReportMatrix(ReportMatrix):
    """
    Render a matrix report as html
    """

    outdir: str

    def __init__(self, outdir: str):
        super(HtmlReportMatrix, self).__init__()
        self.outdir = outdir

    def add_report(self, filename: str, show_toc: bool=True):
        """
        Load a report
        """
        super(HtmlReportMatrix, self).add_report(filename)
        basename = os.path.basename(filename)
        # make the individual report too
        report = self.reports[basename].html(show_toc=show_toc)
        if self.outdir != "" and not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        with open(
                os.path.join(self.outdir, basename) + ".html", "wb") as filehandle:
            filehandle.write(report.encode("utf-8"))

    def short_outcome(self, outcome: CaseResult) -> "Literal['ok', '/', 's', 'f', 'F', '%', 'X', 'U', '?']":
        if outcome == CaseResult.PASSED:
            return "ok"
        return super(HtmlReportMatrix, self).short_outcome(outcome)

    def short_axis(self, axis: str):
        if axis.endswith(".xml"):
            return axis[:-4]
        return axis

    def summary(self, template: "Optional[Any]"=None):
        """
        Render the html
        :return:
        """
        html_matrix = HTMLMatrix(self, template)

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
                testcase: "Optional[Case]" = None
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

                if testcase is None or testcase.name is None:
                    testcase_name = ""
                else:
                    testcase_name = testcase.name
                combined, combined_name = self.combined_result(
                    self.case_results[classname][testcase_name])

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
