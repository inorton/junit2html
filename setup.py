from distutils.core import setup

files = ["*.css"]


setup(
    name="junit2html",
    version="0.1.0",
    description="Generate HTML reports from Junit results",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/inorton/junit2html",
    packages=["junit2htmlreport"],
    package_data={"junit2htmlreport": files},
    entry_points={'console_scripts': ['junit2html=junit2htmlreport.runner:start']},
    platforms=["any"],
    license="License :: OSI Approved :: MIT License",
    long_description="Genearate a single file HTML report from a Junit XML file"
)
