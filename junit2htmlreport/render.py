"""
Render junit reports as HTML
"""
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader


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
    def __init__(self, matrix, template=None):
        self.title = "JUnit Matrix"
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
