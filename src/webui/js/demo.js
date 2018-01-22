define([], function() {

    function handleRequest(url, args, callback) {

        var response = { errcode: 0 };
        var result = {};

        {
            response.errcode = 1;
            result = 'Please run start-server.bat or start-server.sh first.'
        }

        response.result = result;
        callback(response);

    }

    return {

        handleRequest: handleRequest,

    }

});
