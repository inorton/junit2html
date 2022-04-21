import os
from setuptools import setup


files = [os.path.join("templates", "*.css"),
         os.path.join("templates", "*.html")]


setup(
    name="junit2html",
    version="30.1.3",
    description="Generate HTML reports from Junit results",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/inorton/junit2html",
    install_requires=["jinja2>=3.0"],
    packages=["junit2htmlreport"],
    package_data={"junit2htmlreport": files},
    entry_points={'console_scripts': ['junit2html=junit2htmlreport.runner:start']},
    platforms=["any"],
    license="License :: OSI Approved :: MIT License",
    long_description="Genearate a single file HTML report from a Junit or XUnit XML results file"
)
