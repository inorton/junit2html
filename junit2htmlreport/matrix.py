"""
Handle multiple parsed junit reports
"""
from __future__ import unicode_literals
import os
from junit2htmlreport import parser


class ReportMatrix(object):
    """
    Load and handle several report files
    """

    def __init__(self):
        self.reports = {}
        self.cases = {}
        self.classes = {}
        self.casenames = {}

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

    def summary(self):
        """
        Render a summary of the matrix
        :return:
        """
        raise NotImplementedError()


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
        with open(os.path.join(self.outdir, basename) + ".html", "w") as filehandle:
            filehandle.write(report)

    def summary(self):
        """
        Render the html
        :return:
        """
        output = self.get_html_head("")
        output += "<body>"
        output += "<h2>Reports Matrix</h2><hr size='1'/>"

        # table headers
        output += "<table><tr><td></td>"
        for axis in self.reports:
            label = axis
            if label.endswith(".xml"):
                label = label[:-4]
            output += "<th><p class='slanted'>{}</p></th>".format(label)
        output += "</tr>"

        # iterate each class
        for classname in self.classes:
            # new class
            output += "<tr><td colspan='{}'>{}</td></tr>\n".format(
                len(self.reports),
                classname)

            # print the case name
            for casename in sorted(set(self.casenames[classname])):
                output += "<tr><td>- {}</td>".format(casename)

                # print each test and its result for each axis
                for axis in self.reports:
                    cellclass = "absent"
                    anchor = None
                    if axis not in self.cases[classname][casename]:
                        cell = "&nbsp;"
                    else:
                        testcase = self.cases[classname][casename][axis]
                        anchor = testcase.anchor()
                        if testcase.skipped:
                            cell = "s"
                            cellclass = "skipped"
                        elif testcase.failure:
                            cell = "f"
                            cellclass = "failed"
                        else:
                            cell = "ok"
                            cellclass = "passed"

                    cell = "<a href='{}.html#{}'>{}</a>".format(
                        axis, anchor, cell
                    )
                    output += "<td align='middle' class='{}'>{}</td>".format(cellclass,
                                                                             cell)
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
        for filename in self.reports:
            output += "{}    {}{}\n".format(" " * left_indent, treelines, filename)
            treelines += "| "
        output += "{}    {}\n".format(" " * left_indent, treelines)
        # render in groups of the same class

        for classname in self.classes:
            # new class
            output += "{}  \n".format(classname)

            # print the case name
            for casename in sorted(set(self.casenames[classname])):
                output += "- {}{}  ".format(casename, " " * (left_indent - len(casename)))

                # print each test and its result for each axis
                for axis in self.reports:
                    if axis not in self.cases[classname][casename]:
                        output += "- "
                    else:
                        testcase = self.cases[classname][casename][axis]
                        if testcase.skipped:
                            output += "s "
                        elif testcase.failure:
                            output += "f "
                        else:
                            output += "/ "

                output += "\n"
        return output