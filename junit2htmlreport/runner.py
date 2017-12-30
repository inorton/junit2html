"""
Small command line tool to generate a html version of a junit report file
"""

from optparse import OptionParser
import sys
from junit2htmlreport import parser, matrix


USAGE = "usage: %prog [OPTIONS] JUNIT_XML_REPORT [OUTFILE]"
PARSER = OptionParser(usage=USAGE, prog="junit2html")

PARSER.add_option("--summary-matrix", dest="text_matrix", action="store_true",
                  default=False,
                  help="Render multiple result files to the console")


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

    if opts.text_matrix:
        merge = matrix.TextReportMatrix()
        for filename in args:
            merge.add_report(filename)
        print(merge.summary())
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
