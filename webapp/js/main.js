define(['settings', 'utils', 'connector', 'project'], function (settings, utils, conn, project) {

    document.getElementById('check_bind_harddisk').addEventListener('change', function (e) {
        e.target.checked
            ? document.getElementById('input_bind_harddisk').removeAttribute('disabled')
            : document.getElementById('input_bind_harddisk').setAttribute('disabled', '1');
    }, false);

    document.getElementById('check_expired_date').addEventListener('change', function (e) {
        e.target.checked
            ? document.getElementById('input_expired_date').removeAttribute('disabled')
            : document.getElementById('input_expired_date').setAttribute('disabled', '1');
    }, false);

    document.getElementById('new-project').addEventListener('click', project.newProject, false);
    document.getElementById('open-project').addEventListener('click', project.openProjectModal, false);
    document.getElementById('save-project').addEventListener('click', project.saveProject, false);
    document.getElementById('build-project').addEventListener('click', project.buildProject, false);

    document.getElementById('new-license').addEventListener('click', project.newLicense, false);
    document.getElementById('remove-license').addEventListener('click', project.removeLicense, false);

    document.getElementById('project-manage-open').addEventListener('click', project.openProject, false);
    document.getElementById('project-manage-remove').addEventListener('click', project.removeProject, false);

    utils.loadPage('tutorial.html', function (text) {
        document.getElementById('documentation').firstElementChild.innerHTML = text;
        document.getElementById('documentation').querySelector('h1').remove();
    });

    conn.queryVersion(
        function (response) {
            settings.demoFlag = false;
            if (response.errcode)
                utils.showMessage(response.result);
            else
                settings.setVersionInfo(response.result);
            project.initProject();
        },

        function (event) {
            settings.demoFlag = true;
            settings.setDemoInfo();
            project.initProject();
        }
    );

});
