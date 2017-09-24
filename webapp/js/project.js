define(['connector', 'utils'], function(conn, utils) {

    var _project = undefined;
    var _key = 'dashingsoft.pyarmor.project.name';
    var _projectList = document.getElementById('project-manage-list');

    function loadProject(data) {
        document.getElementById('input_project_name').value = data.name;
        document.getElementById('input_project_title').value = data.title;
        document.getElementById('input_project_capsule').value = data.capsule;
        document.getElementById('input_project_path').value = data.path;
        document.getElementById('input_project_files').value = data.files;
        document.getElementById('input_project_scripts').value = data.scripts;

        document.getElementById('input_project_clean').checked = data.clean;
        document.getElementById('input_build_path').value = data.output;
        document.getElementById('input_project_target').value = data.target;

        document.getElementById('check_bind_harddisk').value = '';
        document.getElementById('check_expired_date').value = '';
        document.getElementById('input_bind_harddisk').value = '';
        document.getElementById('input_expired_date').value = '';
        document.getElementById('input_license_rcode').value = '';

        var default_license = data.default_license;
        var options = ['<option value=""' + (default_license === '' ? ' selected' : '') +
                       '>Run in any machine and never expired</option>'];
        for (var i=0; i < data.licenses.length; i++) {
            var title = data.licenses[i].title;
            var filename = data.licenses[i].filename;
            options.push('<option value="' + filename + '"' +
                         (default_license === filename ? ' selected' : '') + '>' +
                         title + '(' + filename + ')</option>');
        }
        document.getElementById('input_project_licenses').innerHTML = options.join('');
        document.getElementById('input_project_default_license').innerHTML = options.join('');

        _project = data;
        window.localStorage.setItem(_key, data.name);
        $('#project a[href="#project-basic"]').tab('show');
    }

    function _updateProject() {
        _project.name = document.getElementById('input_project_name').value;
        _project.title = document.getElementById('input_project_title').value;
        _project.capsule = document.getElementById('input_project_capsule').value;
        _project.path = document.getElementById('input_project_path').value;
        _project.files = document.getElementById('input_project_files').value;
        _project.scripts = document.getElementById('input_project_scripts').value;
        _project.target = document.getElementById('input_project_target').value;
        _project.default_license  = document.getElementById('input_project_default_license').value;
        _project.clean = document.getElementById('input_project_clean').checked;
        _project.output = document.getElementById('input_build_path').value;
    }

    function newProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            result = response.result;
            loadProject(result.project);
        }
        conn.newProject(_callback);
    }

    function saveProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            utils.showMessage(response.result);
        }

        _updateProject();
        conn.updateProject(_project, _callback);
    }

    function buildProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            utils.showMessage(response.result);
        }

        _updateProject();
        conn.buildProject(_project, _callback);
    }

    function openProjectModal() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
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
        }
        conn.queryProject({}, _callback);
    }

    function openProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            result = response.result;
            loadProject(result.project);
        }
        var index = _projectList.selectedIndex;
        if (index !== -1)
            conn.queryProject({name: _projectList.value}, _callback);
        $('#project-manage-modal').modal('hide');
    }

    function removeProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            _projectList.remove(index);
            utils.showMessage(response.result);
        }
        var index = _projectList.selectedIndex;
        if (index !== -1)
            conn.removeProject({name: _projectList.value}, _callback);
    }

    function newLicense() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            var result = response.result;
            _project.licenses.push(result);

            var opt = document.createElement("option");
            opt.text = result.title + ' (' + result.filename + ')';
            opt.value = result.filename;
            document.getElementById('input_project_licenses').add(opt);
            document.getElementById('input_project_default_license').add(opt.cloneNode(true));
            utils.showMessage('New license ' + result.title + ' OK.');
        }

        var args = {};
        var value;
        if (document.getElementById('check_bind_harddisk').checked) {
            value = document.getElementById('input_bind_harddisk').value;
            if (value == '') {
                utils.showMessage('Serial number of harddisk is requried.');
                document.getElementById('input_bind_harddisk').focus();
                return;
            }
            args.hdinfo = value;
        }
        if (document.getElementById('check_expired_date').checked) {
            value = document.getElementById('input_expired_date').value;
            if (value == '') {
                utils.showMessage('Expired date is required.');
                document.getElementById('input_expired_date').focus();
                return;
            }
            args.expired = value;
        }
        if (args.hdinfo === undefined && args.expired === undefined) {
            args.rcode = document.getElementById('input_license_rcode').value;
            if (args.rcode === '') {
                utils.showMessage('All input is blank, at least one is required.');
                return;
            }
        }

        args.name = _project.name;
        conn.newLicense(args, _callback);
    }

    function removeLicense(e) {
        var licenseList = document.getElementById('input_project_licenses');
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result);
                return ;
            }
            _project.licenses.pop(index - 1);
            licenseList.remove(index);
            utils.showMessage(response.result);

            var element = document.getElementById('input_project_default_license');
            element.remove(index)
            if (index == element.selectedIndex)
                element.selectedIndex = 0;
        }
        var index = licenseList.selectedIndex;
        if (index > 0) {
            args = {
                name: _project.name,
                filename: licenseList.value,
                index: index - 1
            }
            conn.removeLicense(args, _callback);
        }
        else if (index === 0)
            utils.showMessage('Default license can not be removed.');
    }

    // Load default project when webapp start
    function initProject() {
        var _callback = function (response) {
            if (response.errcode) {
                utils.showMessage(response.result + '<p>Click button New to start');
                window.localStorage.clear();
                return ;
            }
            result = response.result;
            loadProject(result.project);
        }

        var name = window.localStorage.getItem(_key);
        if (name === undefined || name === null || name === '') {
            $('#navbar-main-tab a[href="#home"]').tab('show');
            conn.newProject(_callback);
        }
        else
            conn.queryProject({ name: name }, _callback);
    }

    return {
        currentProject: _project,

        loadProject: loadProject,
        initProject: initProject,
        newProject: newProject,
        openProjectModal: openProjectModal,
        openProject: openProject,
        saveProject: saveProject,
        buildProject: buildProject,
        removeProject: removeProject,
        newLicense: newLicense,
        removeLicense: removeLicense,
    }

});
