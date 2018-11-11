define([], function() {

    if (typeof String.prototype.trim === 'undefined')
        String.prototype.trim = function() {
            return this.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
        };

    var _element = document.getElementById('global-message');
    var showMessage = function (msg, type) {
        _element.innerHTML =
            '<div class="alert alert-' + (type === 'error' ? 'danger' : 'success') + ' alert-dismissible" role="alert">' +
            '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
            msg +
            '</div>';
        _element.style.display = 'block';

        logMessage(msg);
    };

    document.addEventListener('click', function (e) {
        if (e.target.tagName !== 'BUTTON' || e.target.className === 'close')
            _element.style.display = 'none';
    }, false);

    var _logElement = document.getElementById('project-log-message');
    var logMessage = function (msg) {
        _logElement.value += msg.replace('<p>', '\n') + '\n';
    };
    document.getElementById('clear-log-message').addEventListener('click', function (e) {
        e.preventDefault();
        _logElement.value = '';
    }, false);

    var loadPage = function (url, callback) {
        var request = new XMLHttpRequest();
        request.onerror = function (e) {
            callback('<a href="' + url + '">' + url + '</a>');
        };
        request.onload = function() {
            callback(request.responseText);
        };
        request.open('GET', url, true);
        request.send();
    };

    return {
        logMessage: logMessage,
        showMessage: showMessage,
        showError: function (msg) { showMessage(msg, 'error'); },
        loadPage: loadPage
    };

});
