junit2html by Ian Norton <inorton@gmail.com>
-------------------------------------------------------------

This is a simple self-contained python tool to
produce a single html file from a single junit xml file.

Usage:

```
$ junit2html JUNIT_XML_FILE [NEW_HTML_FILE]
```

eg:

```
$ junit2html pytest-results.xml testrun.html
```
or
```
$ python -m junit2htmlreport pytest-results.xml
```

Installation
------------
```
$ sudo python setup.py install
```
or
```
$ sudo pip install junit2html
```

Example Outputs
---------------

You can see junit2html's own test report output content at:

https://gitlab.com/inorton/junit2html/-/jobs/45530532/artifacts/browse


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

The current master branch status of junit2html is [![pipeline status](https://gitlab.com/inorton/junit2html/badges/master/pipeline.svg)](https://gitlab.com/inorton/junit2html/commits/master)

Releases are availible via Pypi using pip


