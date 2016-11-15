"""
Small command line tool to generate a html version of a junit report file
"""

from optparse import OptionParser
import sys
from junit2htmlreport import parser


USAGE = "usage: %prog JUNIT_XML_REPORT [OUTFILE.html]"
PARSER = OptionParser(usage=USAGE, prog="junit2html")


def run(args):
    """
    Run this tool
    :param args:
    :return:
    """
    (opts, args) = PARSER.parse_args(args) if args else  PARSER.parse_args()
    if not len(args):
        PARSER.print_usage()
        sys.exit(1)

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
    run(sys.argv)


if __name__ == "__main__":
    start()
