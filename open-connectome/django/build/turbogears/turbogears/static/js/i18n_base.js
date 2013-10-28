

function _(key) {
    if (typeof(MESSAGES) != "undefined") {
	var v = MESSAGES[key];
	if(v !== undefined) {
	    return v;
	}
    }
    return key;
}