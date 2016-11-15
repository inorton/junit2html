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

Installation
------------

$ sudo python setup.py install

About Junit
-----------

Junit is a widely used java test framework, it happens to produce a fairly
generic formatted test report and many non-java things produce the same files
(eg py.test) or can be converted quite easily to junit xml (cunit reports via 
xslt). The report files are understood by many things like Jenkins and various
 IDEs.

The format of junit files is described here: http://llg.cubic.org/docs/junit/

Testing
-------

Junit2html is kindly tested on Travis:

![Travis CI](https://travis-ci.org/inorton/junit2html.svg?branch=master)
https://travis-ci.org/inorton/junit2html 


