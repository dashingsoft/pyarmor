define(['settings', 'utils', 'connector', 'project'], function (settings, utils, conn, project) {

    // Obfuscate mode
    if (document.getElementById('obfuscator-console')) {
        document.body.addEventListener('click', function (e) {
            if ((e.target.getAttribute('data-target') !== '#navbar-main-tab') && e.target.parentElement
                && (e.target.parentElement.getAttribute('data-target') !== '#navbar-main-tab'))
                document.getElementById('navbar-main-tab').classList.remove('in');
        }, false);
        document.getElementById('obfuscate-scripts').addEventListener('click', project.obfuscateScripts, false);
        document.getElementById('generate-licenses').addEventListener('click', project.generateLicenses, false);
        document.getElementById('pack-obfuscated-scripts').addEventListener('click', project.packObfuscatedScripts, false);

        conn.queryVersion(
            function (response) {
                settings.demoFlag = false;
                if (response.errcode)
                    utils.showMessage(response.result);
                else if (response.result.rcode) {
                    document.querySelector('a.navbar-brand > span').textContent = 'V' + response.result.version;
                }
            },

            function (event) {
                settings.demoFlag = true;
                document.querySelector('a.navbar-brand > span').textContent = 'Demo';
            }
        );

    }
    
    // Project mode
    else {
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
                utils.showMessage( 'This web page does not work in local file mode, please run pyarmor-webui' );
            }
        );
    }

});
