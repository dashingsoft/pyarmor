define(['settings', 'utils'], function(settings, utils) {

    function onError(e) {
        utils.showMessage('Request failed: ' + e);
    }

    function sendRequest(url, args, callback, onerror) {

        var flag = settings.demoFlag;

        if (flag === undefined && !(url === '/queryVersion')) {
            utils.showMessage('Please waiting for a while ...');
            return;
        }
        else if (flag === true) {
            utils.showMessage('Demo version ');
            return;
        }

        var data = JSON.stringify(args);
        utils.logMessage('Request ' + url + ': ' + data)

        var request = new XMLHttpRequest();

        request.onerror = (onerror === undefined) ? onError : onerror;

        request.onload = function() {

            if (request.status != 200) {
                utils.showMessage('Request return : ' + request.status);
                return;
            }

            if (typeof callback === 'function')
                callback(JSON.parse(request.responseText));
        };

        request.open('POST', url, true);
        request.send(data);
    }

    return {

        newProject: function (callback) {
            sendRequest('/newProject', {}, callback)
        },

        updateProject: function (args, callback) {
            sendRequest('/updateProject', args, callback)
        },

        buildProject: function (args, callback) {
            sendRequest('/buildProject', args, callback)
        },

        removeProject: function (args, callback) {
            sendRequest('/removeProject', args, callback)
        },

        queryProject: function (args, callback) {
            sendRequest('/queryProject', args, callback)
        },

        newLicense: function (args, callback) {
            sendRequest('/newLicense', args, callback)
        },

        removeLicense: function (args, callback) {
            sendRequest('/removeLicense', args, callback)
        },

        queryVersion: function (callback, onerror) {
            sendRequest('/queryVersion', {}, callback, onerror)
        },

    }

});
