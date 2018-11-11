define(['settings', 'utils', 'demo'], function(settings, utils, demo) {

    function onError(e) {
        utils.showError('Request failed: ' + e + '\nCheck log messages in command console.');
    }

    function showLoader() {
        var loader = document.querySelector('.pyarmor-loader');
        if (loader) {
            loader.style.display = 'block';
        }
        else {
            var fileref = document.createElement('link');
            fileref.setAttribute("rel","stylesheet");
            fileref.setAttribute("type","text/css");
            fileref.setAttribute("href", 'css/loader.css');
            if(typeof fileref != "undefined"){
                document.getElementsByTagName("head")[0].appendChild(fileref);
            }
            loader = document.createElement('DIV');
            loader.className = 'pyarmor-loader modal-backdrop fade in';
            loader.innerHTML = '<div class="plone-loader"><div class="loader"/></div>';
            document.body.appendChild(loader);
            loader.addEventListener('click', hideLoader, false);
        }
    }

    function hideLoader() {
        var loader = document.querySelector('.pyarmor-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    function sendRequest(url, args, callback, onerror) {

        var flag = settings.demoFlag;
        var data = JSON.stringify(args);

        if (flag === undefined && !(url === '/queryVersion')) {
            utils.showMessage('Please waiting for a while ...');
            return;
        }
        else if (flag === true) {
            utils.logMessage('Request ' + url + ': ' + data);
            demo.handleRequest(url, args, callback);
            return;
        }

        utils.logMessage('Request ' + url + ': ' + data);
        var request = new XMLHttpRequest();

        request.onloadend = hideLoader;
        request.onerror = (onerror === undefined) ? onError : onerror;
        request.onload = function() {

            if (request.status != 200) {
                if (request.responseURL.substr(-12) === 'queryVersion') {
                    request.onerror();
                    return;
                }
                utils.showError('Request ' + request.responseURL + ' return : ' + request.status);
                return;
            }

            if (typeof callback === 'function')
                callback(JSON.parse(request.responseText));
        };

        request.open('POST', url, true);
        request.send(data);

        if (url !== '/queryVersion')
            showLoader();
    }

    return {

        obfuscateScripts: function (args, callback) {
            sendRequest('/obfuscateScripts', args, callback);
        },

        generateLicenses: function (args, callback) {
            sendRequest('/generateLicenses', args, callback);
        },

        packObfuscatedScripts: function (args, callback) {
            sendRequest('/packObfuscatedScripts', args, callback);
        },

        newProject: function (callback) {
            sendRequest('/newProject', {}, callback);
        },

        updateProject: function (args, callback) {
            sendRequest('/updateProject', args, callback);
        },

        buildProject: function (args, callback) {
            sendRequest('/buildProject', args, callback);
        },

        removeProject: function (args, callback) {
            sendRequest('/removeProject', args, callback);
        },

        queryProject: function (args, callback) {
            sendRequest('/queryProject', args, callback);
        },

        newLicense: function (args, callback) {
            sendRequest('/newLicense', args, callback);
        },

        removeLicense: function (args, callback) {
            sendRequest('/removeLicense', args, callback);
        },

        queryVersion: function (callback, onerror) {
            sendRequest('/queryVersion', {}, callback, onerror);
        }

    };

});
