define([], function() {

    var _counter = 0;
    var _projectList = [];

    function defaultProject(n) {
        data = {}
        data.name = 'project-' + n;
        data.title = 'Project ' + n;
        data.path = '/opt/pyarmor/src/examples';
        data.capsule = '';
        data.files = 'include *.py';
        data.scripts = 'main';
        data.output = '/opt/pyarmor/webapp/build';
        data.inplace = 0;
        data.clean = 0;
        data.target = '';
        data.licenses = [];
        data.default_license = '';
        _projectList.push(data);
        return data;
    }

    function getProject(name) {
        for (var i = 0; i < _projectList.length; i ++) {
            if ( _projectList[i].name === name )
                return i;
        }
    }

    function handleRequest(url, args, callback) {

        var response = { errcode: 0 };
        var result = {};

        if (url === '/newProject') {

            _counter ++;
            result.project = defaultProject(_counter);
            result.message = 'Project has been created';            

        }

        else if (url === '/updateProject') {

            var index = getProject(args.name);
            var data = _projectList[index];
            for (var k in args)
                data[k] = args[k];
            result = 'Update project OK';

        }

        else if (url === '/buildProject') {

            result = 'Encrypt project OK.'

        }

        else if (url === '/removeProject') {

            var index = getProject(args.name);
            _projectList.splice(index, 1);
            result = 'Remove project OK'

        }

        else if (url === '/queryProject') {

            if (args.name === undefined) {

                result = []
                for (var i = 0; i < _projectList.length; i++ )
                    result.push({
                        name: _projectList[i].name,
                        title: _projectList[i].title,
                    });

            }

            else {

                var index = getProject(args.name);                
                var n = parseInt(args.name.split('-')[1]);
                if (_counter < n) _counter = n;
                result.project = (index === undefined) ? defaultProject(n) : _projectList[index];
                result.message = 'Got project OK';

            }

        }

        else if (url === '/newLicense') {

            var title = '';
            if (args.hdinfo !== undefined)
                title += 'Bind to ' + args.hdinfo;
            if (args.expired !== undefined)
                title += 'Expired on ' + args.expired;
            if (args.rcode !== undefined)
                title = 'Code: ' + args.rcode;
            result.title = title;
            result.filename = 'projects/' + args.name + '/license-' + _counter + '.lic';
            _counter ++;

        }

        else if (url === '/removeLicense') {
            
            result = 'Remove license OK.'

        }

        else {
            response.errcode = 1;
            result = 'Unrecognized request: ' + url;
        }

        response.result = result;
        callback(response);

    }

    return {

        handleRequest: handleRequest,

    }

});
