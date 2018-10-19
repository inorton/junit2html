"""
Handle multiple parsed junit reports
"""
from __future__ import unicode_literals
import os
from junit2htmlreport import parser
from junit2htmlreport.parser import SKIPPED, FAILED, PASSED, ABSENT

UNTESTED = "untested"
PARTIAL_PASS = "partial pass"
PARTIAL_FAIL = "partial failure"
TOTAL_FAIL = "total failure"


class ReportMatrix(object):
    """
    Load and handle several report files
    """

    def __init__(self):
        self.reports = {}
        self.cases = {}
        self.classes = {}
        self.casenames = {}
        self.result_stats = {}

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
                    if basename not in self.casenames:
                        self.casenames[testclass].append(basename)

                    if testclass not in self.cases:
                        self.cases[testclass] = {}
                    if basename not in self.cases[testclass]:
                        self.cases[testclass][basename] = {}
                    self.cases[testclass][basename][filename] = testcase

                    outcome = testcase.outcome()
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
            if SKIPPED in results:
                return self.short_outcome(PARTIAL_PASS), PARTIAL_PASS.title()
            return self.short_outcome(PASSED), PASSED.title()

        if FAILED in results:
            return self.short_outcome(TOTAL_FAIL), TOTAL_FAIL.title()
        if SKIPPED in results:
            return self.short_outcome(UNTESTED), UNTESTED.title()
        return " ", ""


class HtmlReportMatrix(ReportMatrix, parser.HtmlHeadMixin):
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
        with open(os.path.join(self.outdir, basename) + ".html",
                  "w") as filehandle:
            filehandle.write(report)

    def get_stats_table(self):
        stats = "<table class='result-stats'>"
        for outcome in sorted(self.result_stats.keys()):
            stats += "<tr><th class='{}'>{}<th>" \
                     "<td align='right'>{}</td></tr>".format(
                outcome,
                outcome.title(),
                self.result_stats[outcome]
            )
        stats += "</table>"
        return stats

    def short_outcome(self, outcome):
        if outcome == PASSED:
            return "ok"
        return super(HtmlReportMatrix, self).short_outcome(outcome)

    def summary(self):
        """
        Render the html
        :return:
        """
        output = self.get_html_head("")
        output += "<body>"
        output += "<h2>Reports Matrix</h2><hr size='1'/>"

        # table headers,
        #
        #          report 1
        #          |  report 2
        #          |  |  report 3
        #          |  |  |
        #   test1  f  /  s  % Partial Failure
        #   test2  s  /  -  % Partial Pass
        #   test3  /  /  /  * Pass
        output += "<table class='test-matrix'>"

        def make_underskip(length):
            return "<td align='middle'>&#124;</td>" * length

        spansize = 1 + len(self.reports)
        report_headers = 0

        shown_stats = False

        stats = self.get_stats_table()

        for axis in self.report_order():
            label = axis
            if label.endswith(".xml"):
                label = label[:-4]
            underskip = make_underskip(report_headers)

            header = "<td colspan='{}'><pre>{}</pre></td>".format(spansize,
                                                                  label)
            spansize -= 1
            report_headers += 1
            first_cell = ""
            if not shown_stats:
                # insert the stats table
                first_cell = "<td rowspan='{}'>{}</td>".format(
                    len(self.report_order()),
                    stats
                )
                shown_stats = True

            output += "<tr>{}{}{}</tr>".format(first_cell,
                                               underskip, header)

        output += "<tr><td></td>{}</tr>".format(
            make_underskip(len(self.reports)))

        # iterate each class
        for classname in self.classes:
            # new class
            output += "<tr class='testclass'><td colspan='{}'>{}</td></tr>\n".format(
                len(self.reports) + 2,
                classname)

            # print the case name
            for casename in sorted(set(self.casenames[classname])):
                output += "<tr class='testcase'><td width='16'>-&nbsp;{}</td>".format(casename)

                case_results = []

                # print each test and its result for each axis
                celltds = ""
                for axis in self.report_order():
                    cellclass = ABSENT
                    anchor = None
                    if axis not in self.cases[classname][casename]:
                        cell = "&nbsp;"
                    else:
                        testcase = self.cases[classname][casename][axis]
                        anchor = testcase.anchor()

                        cellclass = testcase.outcome()
                        cell = self.short_outcome(cellclass)
                    case_results.append(cellclass)

                    cell = "<a class='tooltip-parent testcase-link' href='{}.html#{}'>{}{}</a>".format(
                        axis, anchor, cell,
                        "<div class='tooltip'>({}) {}</div>".format(
                            cellclass.title(),
                            axis)
                    )
                    if cellclass == ABSENT:
                        cell = ""

                    celltds += "<td class='testcase-cell {}'>{}</td>".format(
                        cellclass,
                        cell)

                combined_name = self.combined_result(case_results)[1]

                output += celltds
                output += "<td span class='testcase-combined'>{}</td>".format(
                    combined_name
                )
                output += "</tr>"

        output += "</table>"
        output += "</body>"
        output += "</html>"
        return output


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
                case_results = []
                for axis in self.report_order():
                    if axis not in self.cases[classname][casename]:
                        case_data += "  "
                    else:
                        testcase = self.cases[classname][casename][axis]
                        if testcase.skipped:
                            case_data += "s "
                            case_results.append(SKIPPED)
                        elif testcase.failure:
                            case_data += "f "
                            case_results.append(FAILED)
                        else:
                            case_data += "/ "
                            self.append = case_results.append(PASSED)

                combined, combined_name = self.combined_result(case_results)

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
