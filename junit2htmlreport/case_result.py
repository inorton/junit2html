from enum import Enum


class CaseResult(str, Enum):
    UNTESTED = "untested"
    PARTIAL_PASS = "partial pass"
    PARTIAL_FAIL = "partial failure"
    TOTAL_FAIL = "total failure"
    FAILED = "failed"  # the test failed
    SKIPPED = "skipped"  # the test was skipped
    PASSED = "passed"  # the test completed successfully
    ABSENT = "absent"  # the test was known but not run/failed/skipped
    UNKNOWN = ""

    def __str__(self) -> str:
        return self.value
