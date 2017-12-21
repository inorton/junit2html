import sys
if sys.version_info >= (3, 0):
    from . import runner
else:
    import runner
runner.start()
