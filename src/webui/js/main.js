define(['settings', 'utils', 'connector', 'project'], function (settings, utils, conn, project) {

    document.getElementById('enable_project_runtime_path').addEventListener('change', function (e) {
        e.target.checked
            ? document.getElementById('input_project_runtime_path').removeAttribute('disabled')
            : document.getElementById('input_project_runtime_path').setAttribute('disabled', '1');
    }, false);

    document.getElementById('new-project').addEventListener('click', project.newProject, false);
    document.getElementById('open-project').addEventListener('click', project.openProjectModal, false);
    document.getElementById('save-project').addEventListener('click', project.saveProject, false);
    document.getElementById('build-project').addEventListener('click', project.buildProject, false);

    document.getElementById('new-license').addEventListener('click', project.newLicense, false);

    document.getElementById('project-manage-open').addEventListener('click', project.openProject, false);
    document.getElementById('project-manage-remove').addEventListener('click', project.removeProject, false);

    utils.loadPage(document.getElementById('documentation').firstElementChild.textContent, function (text) {
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
            utils.showMessage( 'This web page does not work in local file mode, please run manager.bat or manager.sh.' );
        }
    );

});
