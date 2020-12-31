"""
Render junit reports as HTML
"""
from jinja2 import Environment, PackageLoader, select_autoescape


class HTMLReport(object):
    def __init__(self):
        self.title = ""
        self.report = None

    def load(self, report, title="JUnit2HTML Report"):
        self.report = report
        self.title = title

    def __iter__(self):
        return self.report.__iter__()

    def __str__(self) -> str:
        env = Environment(
            loader=PackageLoader("junit2htmlreport", "templates"),
            autoescape=select_autoescape(["html"])
        )

        template = env.get_template("report.html")
        return template.render(report=self, title=self.title)


class HTMLMatrix(object):
    def __init__(self, matrix):
        self.title = "JUnit Matrix"
        self.matrix = matrix

    def __str__(self) -> str:
        env = Environment(
            loader=PackageLoader("junit2htmlreport", "templates"),
            autoescape=select_autoescape(["html"])
        )

        template = env.get_template("matrix.html")
        return template.render(matrix=self.matrix, title=self.title)
