define(['connector', 'utils'], function(conn, utils) {

    var _project = undefined;
    var _key = 'dashingsoft.pyarmor.project.name';
    var _projectList = document.getElementById('project-manage-list');

    function loadProject(data) {
        document.getElementById('input_project_name').value = data.name;
        document.getElementById('input_project_title').value = data.title;
        document.getElementById('input_project_src').value = data.src;
        document.getElementById('input_project_manifest').value = data.manifest;
        document.getElementById('input_project_entry').value = data.entry;
        document.getElementById('input_project_output').value = data.output;

        document.getElementById('enable_project_runtime_path').checked = data.runtime_path !== null;
        document.getElementById('input_project_runtime_path').value = data.runtime_path;
        document.getElementById('input_project_obf_module_mode').value = data.obf_module_mode;
        document.getElementById('input_project_obf_code_mode').value = data.obf_code_mode;
        document.getElementById('input_project_disable_restrict_mode').value = data.disable_restrict_mode ? '1' : '0';

        document.getElementById('input_expired_date').value = '';
        document.getElementById('input_bind_disk').value = '';
        document.getElementById('input_bind_mac').value = '';
        document.getElementById('input_bind_ipv4').value = '';
        document.getElementById('input_license_rcode').value = '';

        _project = data;
        window.localStorage.setItem(_key, data.name);
        $('#project a[href="#project-basic"]').tab('show');
    }

    function _updateProject() {
        _project.name = document.getElementById('input_project_name').value;
        _project.title = document.getElementById('input_project_title').value;
        _project.src = document.getElementById('input_project_src').value;
        _project.manifest = document.getElementById('input_project_manifest').value;
        _project.entry = document.getElementById('input_project_entry').value;
        _project.output = document.getElementById('input_project_output').value;
        _project.runtime_path = document.getElementById('enable_project_runtime_path').checked ? document.getElementById('input_project_runtime_path').value : null;
        _project.obf_module_mode = document.getElementById('input_project_obf_module_mode').value;
        _project.obf_code_mode = document.getElementById('input_project_obf_code_mode').value;
        _project.disable_restrict_mode = parseInt(document.getElementById('input_project_disable_restrict_mode').value);
    }

    function newProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            loadProject(result.project);
        };
        conn.newProject(_callback);
    }

    function saveProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            utils.showMessage(response.result);
        };

        _updateProject();
        conn.updateProject(_project, _callback);
    }

    function buildProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            utils.showMessage(response.result);
        };

        _updateProject();
        conn.buildProject(_project, _callback);
    }

    function openProjectModal() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            var options = [];
            var currentName = _project.name;
            for (var i = 0; i < result.length; i ++) {
                var name = result[i].name;
                if (name === currentName)
                    continue;
                var title = result[i].title;
                options.push('<option value="' + name + '">' + name + ': ' + title + '</option>');
            }
            options.sort();
            _projectList.innerHTML = options.join('');
            $('#project-manage-modal').modal('show');
        };
        conn.queryProject({}, _callback);
    }

    function openProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            loadProject(result.project);
        };
        var index = _projectList.selectedIndex;
        if (index !== -1)
            conn.queryProject({name: _projectList.value}, _callback);
        $('#project-manage-modal').modal('hide');
    }

    function removeProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            _projectList.remove(index);
            utils.showMessage(response.result);
        };
        var index = _projectList.selectedIndex;
        if (index !== -1)
            conn.removeProject({name: _projectList.value}, _callback);
    }

    function newLicense() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            utils.showMessage('Generate license "' + result.filename + '" OK.');
        };

        if (document.getElementById('input_license_rcode').value === '') {
            utils.showError('Registration code can not be empty!');
            return;
        }

        var args = {};
        args.expired = document.getElementById('input_expired_date').value;
        args.bind_disk = document.getElementById('input_bind_disk').value;
        args.bind_ipv4 = document.getElementById('input_bind_ipv4').value;
        args.bind_mac = document.getElementById('input_bind_mac').value;
        args.rcode = document.getElementById('input_license_rcode').value;
        args.name = _project.name;
        conn.newLicense(args, _callback);
    }

    // Load default project when webapp start
    function initProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result + '<p>Click button New to start');
                window.localStorage.clear();
                return ;
            }
            $('#navbar-main-tab a[href="#project"]').tab('show');
            var result = response.result;
            loadProject(result.project);
        };

        var name = window.localStorage.getItem(_key);
        if (name === undefined || name === null || name === '') {
            conn.newProject(_callback);
        }
        else
            conn.queryProject({ name: name }, _callback);
    }

    function obfuscateScripts() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            utils.showMessage('Obfuscate scripts to "' + result.output + '" OK.');
        };
        var args = {};
        args.src = document.getElementById('input_src').value;
        args.entry = document.getElementById('input_entry').value;
        args.output = document.getElementById('input_output').value;

        // if (!args.src) {
        //     document.getElementById('input_src').focus();
        //     return ;
        // }

        if (!args.entry) {
            document.getElementById('input_entry').focus();
            return ;
        }

        conn.obfuscateScripts(args, _callback);
    }

    function generateLicenses() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            utils.showMessage('Generate license "' + result.output + '" OK.');
        };
        var args = {};
        args.expired = document.getElementById('input_expired_date').value;
        args.bind_disk = document.getElementById('input_bind_disk').value;
        args.bind_ipv4 = document.getElementById('input_bind_ipv4').value;
        args.bind_mac = document.getElementById('input_bind_mac').value;
        args.rcode = document.getElementById('input_license_rcode').value;

        if (!args.rcode) {
            document.getElementById('input_license_rcode').focus();
            return ;
        }

        conn.generateLicenses(args, _callback);
    }

    function packObfuscatedScripts() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showError(response.result);
                return ;
            }
            var result = response.result;
            utils.showMessage('Pack obfuscated scripts into "' + result.output + '" successfully');
        };
        var args = {};
        args.type = document.getElementById('input_packer_type').value;
        args.entry = document.getElementById('input_packer_entry').value;
        args.setup = document.getElementById('input_packer_setup').value;
        args.output = document.getElementById('input_packer_output').value;

        if (!args.entry) {
            document.getElementById('input_packer_entry').focus();
            return ;
        }

        conn.packObfuscatedScripts(args, _callback);
    }

    return {
        currentProject: _project,

        obfuscateScripts: obfuscateScripts,
        generateLicenses: generateLicenses,
        packObfuscatedScripts: packObfuscatedScripts,

        loadProject: loadProject,
        initProject: initProject,
        newProject: newProject,
        openProjectModal: openProjectModal,
        openProject: openProject,
        saveProject: saveProject,
        buildProject: buildProject,
        removeProject: removeProject,
        newLicense: newLicense
    };

});
