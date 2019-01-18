define([], function() {

    function setDemoInfo() {
        var element = document.getElementById('version-info');
        element.innerHTML = 'PyArmor Demo Version';
        document.querySelector('.navbar-brand').innerHTML = 'PyArmor Demo';
    }

    function setVersionInfo(data) {
        var version = data.version;
        var rcode = data.rcode;
        var element = document.getElementById('version-info');
        element.innerHTML = 'PyArmor ' + (rcode === '' ? 'Trial ' : '') + version;
        if (rcode !== '') {
            $('#navbar-main-tab a[aria-controls="purchase"]').addClass('hidden');
        }
    }

    return {
        demoFlag: undefined,
        setDemoInfo: setDemoInfo,
        setVersionInfo: setVersionInfo
    };

});
