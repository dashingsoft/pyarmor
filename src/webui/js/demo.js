define([], function() {

    function handleRequest(url, args, callback) {

        var response = { errcode: 0 };
        var result = {};

        {
            response.errcode = 1;
            result = 'This web page does not work in local file mode, please run manager.bat or manager.sh.'
        }

        response.result = result;
        callback(response);

    }

    return {

        handleRequest: handleRequest,

    }

});
