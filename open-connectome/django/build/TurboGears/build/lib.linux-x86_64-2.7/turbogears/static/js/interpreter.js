/*

    Interpreter: Turbogears Python Interactive Interpreter
    Based heavily on the Javascript Interactive Interpreter MochiKit Demo

*/
InterpreterManager = function () {
    bindMethods(this);
};

InterpreterManager.prototype.initialize = function () {
    updateNodeAttributes('interpreter_text', {
        'onkeyup': this.keyUp
    });
    updateNodeAttributes('interpreter_form', {
        'onsubmit': this.submit
    });
    updateNodeAttributes('exec', {
        'onclick': this.multilineSubmit
    });
    this.banner();
    this.lines = [];
    this.history = [];
    this.currentHistory = '';
    this.historyPos = -1;
};

InterpreterManager.prototype.banner = function () {
    var _ua = window.navigator.userAgent;
    var ua = _ua.replace(/^Mozilla\/.*?\(.*?\)\s*/, '');
    if (ua == '') {
        // MSIE
        ua = _ua.replace(/^Mozilla\/4\.0 \(compatible; MS(IE .*?);.*$/, '$1');
    }
    appendChildNodes('interpreter_output',
        SPAN({'class': 'banner'},
            'TurboGears Console via MochiKit v' + MochiKit.Base.VERSION + ' [' + ua + ']'
        ),
        BR()
    );
};

InterpreterManager.prototype.submit = function () {
    this.doSubmit();
    this.doScroll();
    return false;
};

InterpreterManager.prototype.multilineSubmit = function () {
    this.doMultilineSubmit();
    this.doScroll();
    return false;
};

InterpreterManager.prototype.doScroll = function () {
    var p = getElement('interpreter_output').lastChild;
    if (typeof(p) == 'undefined' || p == null) {
        return;
    }
    var area = getElement('interpreter_area');
    if (area.offsetHeight > area.scrollHeight) {
        area.scrollTop = 0;
    } else {
        area.scrollTop = area.scrollHeight;
    }
};

InterpreterManager.prototype.moveHistory = function (dir) {
    // totally bogus value
    if (dir == 0 || this.history.length == 0) {
        return;
    }
    var elem = getElement('interpreter_text');
    if (this.historyPos == -1) {
        this.currentHistory = elem.value;
        if (dir > 0) {
            return;
        }
        this.historyPos = this.history.length - 1;
        elem.value = this.history[this.historyPos];
        return;
    }
    if (this.historyPos == 0 && dir < 0) {
        return;
    }
    if (this.historyPos == this.history.length - 1 && dir > 0) {
        this.historyPos = -1;
        elem.value = this.currentHistory;
        return;
    }
    this.historyPos += dir;
    elem.value = this.history[this.historyPos];
};

InterpreterManager.prototype.keyUp = function (e) {
    e = e || window.event;
    switch (e.keyCode) {
        case 38: this.moveHistory(-1); break;
        case 40: this.moveHistory(1); break;
        default: return true;
    }
    e.cancelBubble = true;
    return false;
};

InterpreterManager.prototype.doSubmit = function () {
    var elem = getElement('interpreter_text');
    var code = elem.value;
    elem.value = '';

    this.history.push(code);
    this.historyPos = -1;
    this.currentHistory = '';

    var d = loadJSONDoc('process_request?line=' + encodeURIComponent(code));
    d.addCallback(this.showResult);

    return;
};

InterpreterManager.prototype.doMultilineSubmit = function () {
    var elem = getElement('interpreter_block_text');
    var code = elem.value;
    elem.value = '';

    lines = code.split('\n');

    for (var i = 0; i < lines.length; i++) {
        this.history.push(lines[i]);
    }
    this.historyPos = -1;
    this.currentHistory = '';

    var d = loadJSONDoc('process_multiline_request?block=' + encodeURIComponent(code));
    d.addCallback(this.showResult);

    return;
}

InterpreterManager.prototype.showResult = function (res) {
    var lines = res['output'].split('\n');
    for (var i = 0; i < lines.length; i++) {
        var lineclass = 'data';

        // highlight input code.
        // assumption: only input code starts with '>>> ' or '... '
        var lineprefix = lines[i].substr(0,4);
        if (lineprefix == '>>> ' || lineprefix == '... ') {
            lineclass = 'code';
        }

        appendChildNodes('interpreter_output',
            SPAN({'class': lineclass}, lines[i]), BR()
        );
    }

    this.doScroll();
    $('prompt').innerHTML = res['more'] ? '... ' : '>>> ';
};

interpreterManager = new InterpreterManager();
addLoadEvent(interpreterManager.initialize);
