"""
Render junit reports as HTML
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from .matrix import ReportMatrix
    from .parser import Junit
    from os import PathLike
    from typing import Union, Sequence, Optional

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader


class HTMLReport(object):
    title: str = ""
    report: "Optional[Junit]" = None
    show_toc: bool = True

    def __init__(self, show_toc: bool=True):
        self.show_toc = show_toc

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
        return template.render(report=self, title=self.title, show_toc=self.show_toc)


class HTMLMatrix(object):
    title: str = "JUnit Matrix"
    matrix: "ReportMatrix"
    template: "Optional[Union[str,PathLike[str],Sequence[Union[str,PathLike[str]]]]]"

    def __init__(self, matrix: "ReportMatrix", template:"Optional[Union[str,PathLike[str],Sequence[Union[str,PathLike[str]]]]]"=None):
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
