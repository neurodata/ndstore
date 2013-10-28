function AjaxGrid(refresh_url, target_id) {
    bindMethods(this);
    this.refresh_url = refresh_url;
    this.target_id = target_id;
}

AjaxGrid.prototype.refresh = function(params) {
    /***

    Refresh the target DOM with new data from the server

    @param params: extra args to append to the request.
        Example:
            {'sort':'desc', 'offset'=20}

    @rtype: L{Deferred} returning the evaluated JSON response.

    ***/

    params = eval(params);
    params['tg_random'] = new Date().getTime();
    params['tg_format'] = 'json';
    var d = loadJSONDoc(this.refresh_url, params);
    d.addCallback(this.updateGrid);
    return d;
}

AjaxGrid.prototype.updateGrid = function(response) {
    var grid = Widget.grid.render(this.target_id, response);
    swapDOM(this.target_id, grid);
}
