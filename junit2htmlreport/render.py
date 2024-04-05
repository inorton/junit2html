"""
Render junit reports as HTML
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .matrix import ReportMatrix
    from .parser import Junit

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader


class HTMLReport(object):
    title: str = ""
    report: "Junit|None" = None

    def load(self, report: "Junit", title: str="JUnit2HTML Report"):
        self.report = report
        self.title = title

    def __iter__(self):
        if self.report is None:
            raise Exception("A report must be loaded through `load(...)` first.")

        return self.report.__iter__()

    def __str__(self) -> str:
        env = Environment(
            loader=PackageLoader("junit2htmlreport", "templates"),
            autoescape=select_autoescape(["html"])
        )

        template = env.get_template("report.html")
        return template.render(report=self, title=self.title)


class HTMLMatrix(object):
    title: str = "JUnit Matrix"
    matrix: "ReportMatrix"

    def __init__(self, matrix: "ReportMatrix", template=None):
        self.matrix = matrix
        self.template = template

    def __str__(self) -> str:
        if self.template:
            loader = FileSystemLoader(self.template)
        else:
            loader = PackageLoader("junit2htmlreport", "templates")
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html"])
        )

        template = env.get_template("matrix.html")
        return template.render(matrix=self.matrix, title=self.title)
