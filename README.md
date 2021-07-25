junit2html by Ian Norton <inorton@gmail.com>
-------------------------------------------------------------

Hosted at https://gitlab.com/inorton/junit2html 

This is a simple self-contained python tool to
produce a single html file from a single junit xml file.

## Basic Usage:

```
$ junit2html JUNIT_XML_FILE [NEW_HTML_FILE]
```
or
```
$ python -m junit2htmlreport JUNIT_XML_FILE [NEW_HTML_FILE]
```

eg:

```
$ junit2html pytest-results.xml testrun.html
```
or
```
$ python -m junit2htmlreport pytest-results.xml
```

## Advanced Usage:

Render Text summary of results

```
junit2html mytest-results.xml --summary-matrix
```

Render Text sumamry of results and exit non-zero on failures

```
junit2html --summary-matrix ./tests/junit-unicode.xml --max-failures 1
```


# Installation

```
$ sudo python setup.py install
```
or
```
$ sudo pip install junit2html
```

## Example Outputs

You can see junit2html's own test report output content at:
https://gitlab.com/inorton/junit2html/-/jobs/artifacts/master/browse?job=python36

An an example of the "matrix" report output can be found at:
https://gitlab.com/inorton/junit2html/-/jobs/artifacts/master/file/tests/matrix-example.html?job=python39


About Junit
-----------

Junit is a widely used java test framework, it happens to produce a fairly
generic formatted test report and many non-java things produce the same files
(eg py.test) or can be converted quite easily to junit xml (cunit reports via 
xslt). The report files are understood by many things like Jenkins and various
 IDEs.

The format of junit files is described here: http://llg.cubic.org/docs/junit/

Source and Releases
-------------------

Junit2html is maintained on gitlab at https://gitlab.com/inorton/junit2html

The current master build status of junit2html is:
 [![pipeline status](https://gitlab.com/inorton/junit2html/badges/master/pipeline.svg)](https://gitlab.com/inorton/junit2html/commits/master)

The current coverage status is:
 [![coverage report](https://gitlab.com/inorton/junit2html/badges/master/coverage.svg)](https://gitlab.com/inorton/junit2html/commits/master)



Releases are availible via Pypi using pip


