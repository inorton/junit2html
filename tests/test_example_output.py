"""
A series of tests that produce different example output
"""

import sys


def test_stderr_only():
    """
    Print some text to stderr
    :return:
    """
    sys.stderr.write("""
    Hello Standard Error
    =====================================

    This is some formatted stderr
    """)


def test_stdout_only():
    """
    Print some text to stderr
    :return:
    """
    sys.stdout.write("""
    Hello Standard Out
    =====================================

    This is some formatted stdout
    """)


def test_stdoe():
    """
    Print some stuff to stderr and stdout
    :return:
    """
    def err(msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")

    def out(msg):
        sys.stdout.write(msg)
        sys.stdout.write("\n")

    for _ in range(3):
        for word in ["Hello", "World"]:
            err("Err " + word)
            out("Out " + word)

