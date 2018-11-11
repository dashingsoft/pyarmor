define([], function() {

    function handleRequest(url, args, callback) {

        var response = { errcode: 0 };
        var result = {};

        if (url === '/obfuscateScripts') {
            result = {
                output: '[Demo]/home/jondy/pyarmor/dist'
            };
        }

        else if (url === '/generateLicenses') {
            result = {
                output: '[Demo]/home/jondy/pyarmor/licenses/Customer-Tom/license.lic'
            };
        }

        // else if (url === '/packObfuscatedScripts') {
        //     result = {
        //         output: '[Demo]/home/project/src/dist'
        //     };
        // }

        else {
            response.errcode = 1;
            result = 'This web page does not work in local file mode, please run pyarmor-webui';
        }

        response.result = result;
        callback(response);

    }

    return {

        handleRequest: handleRequest

    };

});
