define([], function() {

    function setDemoInfo() {
        var demoButton = document.getElementById('demo-button');
        demoButton.className = 'btn btn-warning';
        demoButton.addEventListener('click', function (e) {
            $('#navbar-main-tab a[aria-controls="documentation"]').tab('show');
        }, false);
        element = document.getElementById('version-info');
        element.innerHTML = 'Pyarmor Demo Version';
    }

    function setVersionInfo(data) {
        var version = data.version;
        var rcode = data.rcode;
        element = document.getElementById('version-info');
        element.innerHTML = 'Pyarmor ' + (rcode === '' ? 'Trial ' : '') + version;
        if (rcode !== '') {
            $('#navbar-main-tab a[aria-controls="purchase"]').addClass('hidden');
        }
    }

    return {
        demoFlag: undefined,
        setDemoInfo: setDemoInfo,
        setVersionInfo: setVersionInfo,
    }

});
