var hide = function(element) { element.style.display = 'none';}
var show = function(element) { element.style.display = '';}
var isHidden = function(element) { return element.style.display == 'none';}
var isSelected = function(element) { return element.classList.contains("selected");}
var deselect = function(element) { return element.classList.remove("selected");}
var select = function(element) { return element.classList.add("selected");}
var toggle = function(element) { isHidden(element) ? show(element) : hide(element);};
var toggleTests = function(heading) { toggle(heading.parentNode.children[1]);};
var toggleDetails = function(detailClass) {
    var details = document.querySelectorAll('.' + detailClass);
    for (var i = details.length - 1; i >= 0; i--) { toggle(details[i]);};
};
var hideAll = function(collection) {
    for (var i = collection.length - 1; i >= 0; i--) { hide(collection[i]); };
}
var showAll = function(collection) {
    for (var i = collection.length - 1; i >= 0; i--) { show(collection[i]); };
}
var selectSegment = function(segment) {
    if (isSelected(segment)) return;
    var segments = document.querySelectorAll('#segment-bar > a');
    for (var i = segments.length - 1; i >= 0; i--) { deselect(segments[i]);
};
select(segment);
    if (segment.id == "all-segment") {
        showAll(document.querySelectorAll('.outcome'));
        showAll(document.querySelectorAll('.testclass'));
        showAll(document.querySelectorAll('.testsuite'));
    } else if (segment.id == "failing-segment") {
        hideAll(document.querySelectorAll('.outcome-aborted'));
        hideAll(document.querySelectorAll('.outcome-passed'));
        showAll(document.querySelectorAll('.outcome-failed'));
        hideAll(document.querySelectorAll('.testclass-aborted'));
        hideAll(document.querySelectorAll('.testclass-passed'));
        showAll(document.querySelectorAll('.testclass-failed'));
        hideAll(document.querySelectorAll('.testsuite-passed'));
        hideAll(document.querySelectorAll('.testsuite-aborted'));
        showAll(document.querySelectorAll('.testsuite-failed'));
    } else if (segment.id == "passing-segment") {
        hideAll(document.querySelectorAll('.outcome-aborted'));
        hideAll(document.querySelectorAll('.outcome-failed'));
        showAll(document.querySelectorAll('.outcome-passed'));
        hideAll(document.querySelectorAll('.testclass-aborted'));
        hideAll(document.querySelectorAll('.testclass-failed:not(:has(.outcome-passed))'));
        showAll(document.querySelectorAll('.testclass-passed'));
        hideAll(document.querySelectorAll('.testsuite-aborted'));
        hideAll(document.querySelectorAll('.testsuite-failed:not(:has(.outcome-passed))'));
        showAll(document.querySelectorAll('.testsuite-passed'));
    } else if (segment.id == "aborting-segment") {
        showAll(document.querySelectorAll('.outcome-aborted'));
        hideAll(document.querySelectorAll('.outcome-failed'));
        hideAll(document.querySelectorAll('.outcome-passed'));
        showAll(document.querySelectorAll('.testclass-aborted'));
        hideAll(document.querySelectorAll('.testclass-failed:not(:has(.outcome-aborted))'));
        hideAll(document.querySelectorAll('.testclass-passed:not(:has(.outcome-aborted))'));
        showAll(document.querySelectorAll('.testclass-passed .outcome-aborted'));
        showAll(document.querySelectorAll('.testclass-failed .outcome-aborted'));
        showAll(document.querySelectorAll('.testsuite-aborted'));
        hideAll(document.querySelectorAll('.testsuite-failed:not(:has(.testclass-failed .outcome-aborted)):not(:has(.testclass-passed .outcome-aborted)):not(:has(.testclass-aborted .outcome-aborted))'));
        hideAll(document.querySelectorAll('.testsuite-passed:not(:has(.testclass-passed .outcome-aborted)):not(:has(.testclass-aborted .outcome-aborted))'));
        showAll(document.querySelectorAll('.testsuite-passed .testclass-passed .outcome-aborted))'));
        showAll(document.querySelectorAll('.testsuite-passed .testclass-aborted))'));
        showAll(document.querySelectorAll('.testsuite-failed .testclass-failed .outcome-aborted))'));
        showAll(document.querySelectorAll('.testsuite-failed .testclass-aborted))'));
    }
}