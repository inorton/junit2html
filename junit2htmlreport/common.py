"""
Common code between JUnit2HTML matrix and merge classes
"""
from __future__ import print_function

from typing import TYPE_CHECKING

from .parser import Case, Junit

if TYPE_CHECKING: # pragma: no cover
    from typing import Dict, List


class ReportContainer(object):
    """
    Hold one or more reports
    """
    reports: "Dict[str, Junit]"

    def __init__(self):
        self.reports = {}

    def add_report(self, filename: str) -> None:
        raise NotImplementedError()

    def failures(self):
        """
        Return all the failed test cases
        :return:
        """
        found: "List[Case]" = []
        for report in self.reports:
            for suite in self.reports[report].suites:
                found.extend(suite.failed())

        return found

    def skips(self):
        """
        Return all the skipped test cases
        :return:
        """
        found: "List[Case]" = []
        for report in self.reports:
            for suite in self.reports[report].suites:
                found.extend(suite.skipped())
        return found
