AutoCompleteManager = function (id, textid, hiddenid, searchController, searchParam,
        resultName, onlySuggest, spinnerOnImg, completeDelay, takeFocus, minChars) {
    this.id = id;
    this.textid = textid;
    this.hiddenid = hiddenid;
    this.textField = null;
    this.hiddenField = null;
    this.searchController = searchController;
    this.searchParam = searchParam;
    this.resultName = resultName;
    this.onlySuggest = onlySuggest;
    this.spinnerOnImg = spinnerOnImg;
    this.completeDelay = completeDelay;
    this.takeFocus = takeFocus;
    this.minChars = minChars;
    this.selectedResultRow = 0;
    this.numResultRows = 0;
    this.specialKeyPressed = false;
    this.isShowingResults = false;
    this.hasFocus = false;
    this.sugestionBoxMouseOver = false;
    this.processCount = 0;
    this.lastSearch = null;
    this.spinner = null;
    this.spinnerStatus = 'off';
    this.lastKey = null;
    this.delayedRequest = null;
    this.hasHiddenValue = false;
    this.lastTextResult = null;
    this.lastHiddenResult = null;
    bindMethods(this);
};

AutoCompleteManager.prototype.initialize = function() {
    // Text field must be set after page renders
    this.textField = getElement(this.textid);
    if (this.hiddenid)
        this.hiddenField = getElement(this.hiddenid);
    if (this.spinnerOnImg) {
        this.spinner = getElement('autoCompleteSpinner' + this.id);
        this.spinnerOffImg = getNodeAttribute(this.spinner, 'src');
    }

    updateNodeAttributes(this.textField, {
        'onkeyup': this.theKeyUp,
        'onkeydown': this.theKeyPress,
        'onblur': this.lostFocus,
        'onfocus': this.gotFocus,
        'autocomplete': 'off'
    });

    // Ensure the initial value doesn't get discarded
    this.lastTextResult = this.textField.value;
    if (this.hiddenField)
        this.lastHiddenResult = this.hiddenField.value;
    if (this.takeFocus) {
        this.textField.focus();
        this.gotFocus();
    }
};

AutoCompleteManager.prototype.spinnerToggle = function(newStatus) {
    if (this.spinner && this.spinnerStatus != newStatus) {
        if (this.spinnerStatus == 'on') {
            this.spinnerStatus = 'off';
            this.spinner.src = this.spinnerOffImg;
        } else {
            this.spinnerStatus = 'on';
            this.spinner.src = this.spinnerOnImg;
        }
    }
}

AutoCompleteManager.prototype.lostFocus = function(event) {
    this.hasFocus = false;
    if (!this.sugestionBoxMouseOver || this.lastKey == 9) {
        // We only clear the suggestion box when the mouse is not over it
        // or when the user pressed tab. So if the user clicked an item
        // we don't delete the table before the onClick event happens.
        this.lastKey = null;
        this.clearResults();
    }
}

AutoCompleteManager.prototype.gotFocus = function(event) {
    this.hasFocus = true;
    if (!this.minChars) this.theKeyUp(event);
}

AutoCompleteManager.prototype.theKeyPress = function(event) {
    // Deal with crappy browser implementations
    event = event || window.event;
    var key = event.keyCode || event.which;
    this.lastKey = key;

    // Used to stop processing of further key functions
    this.specialKeyPressed = false;

    // Used when all text is selected then deleted.
    // Getting selected text has major cross browswer problems.
    // This is gross, but if you are smarter then me (most likely) please fix this:
    if (key == 8 || key == 46) {
        checkIfCleared = function checkIfCleared(theManager) {
            if (theManager.textField.value.length == 0) {
                if (this.hiddenField)
                    theManager.hiddenField.value = '';
            }
        }
        callLater(0.1, checkIfCleared, this);
    }

    // Only perform auto complete functions if there are results to do something with
    if (this.numResultRows > 0) {
        // What key was pressed?
        switch(key) {
            // Enter Key
            case 13:
                var autoCompleteSelectedRow = getElement('autoComplete' + this.id + this.selectedResultRow);
                if (this.onlySuggest && autoCompleteSelectedRow == null) {
                    this.clearResults();
                    break;
                }
                var theCell = getElementsByTagAndClassName('TD', null, autoCompleteSelectedRow)[0];
                var theCellHidden;
                if (this.hasHiddenValue)
                    theCellHidden = getElementsByTagAndClassName('TD', null, autoCompleteSelectedRow)[1];
                else
                    theCellHidden = getElementsByTagAndClassName('TD', null, autoCompleteSelectedRow)[0];
                var autoCompleteText = scrapeText(theCell);
                var autoCompleteHidden = scrapeText(theCellHidden);
                this.textField.value = autoCompleteText;
                this.lastTextResult = autoCompleteText;
                if (this.hiddenField)
                    this.hiddenField.value = autoCompleteHidden;
                this.lastHiddenResult = autoCompleteHidden;
                this.clearResults();
                break;
            // Escape Key
            case 27:
                this.clearResults();
                break;
            // Up Key
            case 38:
                if (this.selectedResultRow > 0) this.selectedResultRow--;
                this.updateSelectedResult();
                break;
            // Down Key
            case 40:
                if (this.selectedResultRow < this.numResultRows - (this.selectedResultRow == null ? 0 : 1)) {
                    if (this.selectedResultRow == null)
                        this.selectedResultRow = 0;
                    else
                        this.selectedResultRow++;
                }
                this.updateSelectedResult();
                break;
            default:
                //pass
        }
        // Make sure other functions know we performed an autocomplete function
        if (key == 13 || key == 27 || key == 38 || key == 40)
            this.specialKeyPressed = true;
    }
    return !this.specialKeyPressed;
};

AutoCompleteManager.prototype.updateSelectedResult = function() {
    // Set classes to show currently selected row
    for (var i=0; i<this.numResultRows; i++) {
        if (this.selectedResultRow == i)
            swapElementClass('autoComplete' + this.id + i, 'autoTextNormalRow', 'autoTextSelectedRow');
        else
            swapElementClass('autoComplete' + this.id + i, 'autoTextSelectedRow', 'autoTextNormalRow');
    }
    // Move the cursor to the end of the line
    var value = this.textField.value
    this.textField.value = '';
    this.textField.value = value;
}

AutoCompleteManager.prototype.clearResults = function() {
    // Hide all the results
    hideElement(getElement('autoCompleteResults' + this.id));
    // Clear out our result tracking
    this.selectedResultRow = 0;
    this.numResultRows = 0;
    this.lastSearch = null;
}

AutoCompleteManager.prototype.displayResults = function(result) {
    // if the field lost focus while processing this request, don't do anything
    if (!this.hasFocus) {
        this.updateSelectedResult();
        this.processCount--;
        if (this.processCount == 0) this.spinnerToggle('off');
        return false;
    }
    var fancyTable = TABLE({'class': 'autoTextTable',
        'name': 'autoCompleteTable' + this.id,
        'id': 'autoCompleteTable' + this.id}, null);
    var fancyTableBody = TBODY(null,null);
    // Track number of result rows and reset the selected one to the first
    var textItems = result[this.resultName];
    this.numResultRows = textItems.length;
    if (this.onlySuggest)
        this.selectedResultRow = null;
    else
        this.selectedResultRow = 0;

    // Grab each item out of our JSON request and add it to our table
    this.isShowingResults = false;

    this.hasHiddenValue = isArrayLike(textItems[0]);

    for (var i in textItems) {
        var currentItem = textItems[i];
        var currentItemValue = textItems[i];
        if (this.hasHiddenValue) {
            currentItem = currentItem[0];
            currentItemValue = currentItemValue[1];
        }

        var rowAttrs = {
            'class': 'autoTextNormalRow',
            'name': 'autoComplete' + this.id + i,
            'id': 'autoComplete' + this.id + i,
            'onmouseover': 'AutoCompleteManager' + this.id + '.sugestionBoxMouseOver = true; AutoCompleteManager' + this.id + '.selectedResultRow=' + i + '; AutoCompleteManager' + this.id + '.updateSelectedResult();',
            'onclick': 'p = new Object; p.keyCode=13; AutoCompleteManager' + this.id + '.theKeyPress(p);',
            'onmouseout': 'AutoCompleteManager' + this.id + '.sugestionBoxMouseOver = false; '
        };

        if (typeof result.options!='undefined' && result.options.highlight) {
            var searchedText = currentItem.toLowerCase().match(this.textField.value.toLowerCase());
            var end = searchedText.index + searchedText[0].length;
            var currentRow = TR(rowAttrs, TD(null,
                createDOM('nobr', null, SPAN({'class': 'autoTextHighlight'}, currentItem.substr(searchedText.index, searchedText[0].length)),
                SPAN(null, currentItem.substr(end)))));
            if (this.hasHiddenValue)
                appendChildNodes(currentRow, TD({'class': 'autoTextHidden'}, SPAN(null, currentItemValue)));
        } else {
            var currentRow = TR(rowAttrs, TD(null,
                createDOM('nobr', null, SPAN(null, currentItem))));
            if (this.hasHiddenValue)
                appendChildNodes(currentRow, TD({'class': 'autoTextHidden'}, SPAN(null, currentItemValue)));
        }
        appendChildNodes(fancyTableBody, currentRow);

        // Found at least 1 result
        this.isShowingResults = true;
    }
    appendChildNodes(fancyTable, fancyTableBody);

    // Swap out the old results with the newly created table
    var resultsHolder = getElement('autoCompleteResults' + this.id);
    if (this.isShowingResults) {
        resultsHolder.style.left = getLeft(this.textField) + 'px';
        resultsHolder.style.top = getBottom(this.textField) + 1 + 'px';
        replaceChildNodes(resultsHolder, fancyTable);
        this.updateSelectedResult();
        showElement(resultsHolder);
    } else hideElement(resultsHolder);

    this.processCount--;
    if (this.processCount == 0) this.spinnerToggle('off');
    return true;
}

AutoCompleteManager.prototype.doDelayedRequest = function () {
    this.delayedRequest = null;

    // Check again if less than required chars, then we won't search.
    if (this.minChars && this.textField.value.length < this.minChars) {
        this.clearResults();
        return false;
    }

    // Get what we are searching for
    var resultName = this.resultName;

    this.processCount++;
    this.spinnerToggle('on');

    this.lastSearch = this.textField.value;
    var searchParam = this.searchParam;
    var params = {'tg_format': 'json',
        'tg_random': new Date().getTime()};
    if (searchParam == '*') {
        el = this.textField.form.elements
        for (var i=0; i<el.length; ++i)
            params[el[i].name] = el[i].value;
    } else if (searchParam)
        params[searchParam] = this.textField.value;

    var d = loadJSONDoc(this.searchController + '?' + queryString(params));
    d.addCallback(this.displayResults);
    return true;
}

AutoCompleteManager.prototype.theKeyUp = function(event) {
    // Stop processing if a special key has been pressed. Or if the last search requested the same string
    if (this.specialKeyPressed || (this.textField.value == this.lastSearch)) return false;

    // If this.textField.value has less than required chars,
    // then we don't need to schedule a request. We have to clear the list.
    if (this.minChars && this.textField.value.length < this.minChars) {
        if (this.delayedRequest) this.delayedRequest.cancel();
        this.clearResults();
        return false;
    }

    // If theKeyUp is activated and there is an old JSON request
    // scheduled for execution, cancel the old request and
    // schedule a new one. The cancellation ensures that we won't
    // spam the server with JSON requests.
    if (this.delayedRequest) this.delayedRequest.cancel();

    // Wait this.completeDelay seconds before loading new
    // auto completions.
    this.delayedRequest = callLater(this.completeDelay, this.doDelayedRequest);

    if (this.hiddenField) {
        if (this.lastTextResult == this.textField.value)
            this.hiddenField.value = this.lastHiddenResult;
        else
            this.hiddenField.value = '';
    }

    return true;
};

function getLeft(s) {
    return getParentOffset(s, 'offsetLeft');
}

function getTop(s) {
    return getParentOffset(s, 'offsetTop');
}

function getBottom(s) {
    return s.offsetHeight + getTop(s);
}

if (typeof getStyle != 'function' && typeof computedStyle == 'function')
    getStyle = computedStyle; // MochiKit 1.3.1

function getParentOffset(s, offsetType) {
    var parentOffset=0;
    while (s && getStyle(s, 'position') != 'relative') {
        parentOffset += s[offsetType];
        s = s.offsetParent;
    }
    return parentOffset;
}
