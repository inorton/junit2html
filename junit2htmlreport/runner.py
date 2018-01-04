"""
Small command line tool to generate a html version of a junit report file
"""
import os
from optparse import OptionParser
import sys
from junit2htmlreport import parser, matrix, merge

USAGE = "usage: %prog [OPTIONS] JUNIT_XML_REPORT [OUTFILE]"
PARSER = OptionParser(usage=USAGE, prog="junit2html")

PARSER.add_option("--summary-matrix", dest="text_matrix", action="store_true",
                  default=False,
                  help="Render multiple result files to the console")

PARSER.add_option("--report-matrix", dest="html_matrix", type=str,
                  metavar="REPORT",
                  help="Generate an HTML report matrix")

PARSER.add_option("--merge", dest="merge_output", type=str,
                  metavar="NEWREPORT",
                  help="Merge multiple test results into one file")


def run(args):
    """
    Run this tool
    :param args:
    :return:
    """
    (opts, args) = PARSER.parse_args(args) if args else PARSER.parse_args()
    if not len(args):
        PARSER.print_usage()
        sys.exit(1)

    if opts.merge_output:
        merger = merge.Merger()
        for inputfile in args:
            merger.load_report(inputfile)

        xmltext = merger.toxmlstring()
        with open(opts.merge_output, "w") as outfile:
            outfile.write(xmltext)
    elif opts.text_matrix:
        tmatrix = matrix.TextReportMatrix()
        for filename in args:
            tmatrix.add_report(filename)
        print(tmatrix.summary())
    elif opts.html_matrix:
        hmatrix = matrix.HtmlReportMatrix(os.path.dirname(opts.html_matrix))
        for filename in args:
            hmatrix.add_report(filename)
        with open(opts.html_matrix, "w") as outfile:
            outfile.write(hmatrix.summary())
    else:
        outfilename = args[0] + ".html"
        if len(args) > 1:
            outfilename = args[1]

        report = parser.Junit(args[0])
        html = report.html()

        with open(outfilename, "wb") as outfile:
            outfile.write(html.encode('utf-8'))


def start():
    """
    Run using the current sys.argv
    """
    run(sys.argv[1:])


if __name__ == "__main__":
    start()
