from setuptools import setup

files = ["*.css"]


setup(
    name="junit2html",
    version="2.0.1",
    description="Generate HTML reports from Junit results",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/inorton/junit2html",
    install_requires=["junitparser>=2.0.0b1"],
    packages=["junit2htmlreport"],
    package_data={"junit2htmlreport": files},
    entry_points={'console_scripts': ['junit2html=junit2htmlreport.runner:start']},
    platforms=["any"],
    license="License :: OSI Approved :: MIT License",
    long_description="Genearate a single file HTML report from a Junit or XUnit XML results file"
)
