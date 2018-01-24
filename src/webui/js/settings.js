define([], function() {

    function setDemoInfo() {
        element = document.getElementById('version-info');
        element.innerHTML = 'Pyarmor Demo Version';
        document.querySelector('.navbar-brand').innerHTML = 'Pyarmor Demo';
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
