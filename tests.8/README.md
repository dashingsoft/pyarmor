# V8 Tests

How to run v8 tests?

Make sure Pyarmor 8.0+ is installed, test most of Pyarmor features

    python accept_test.py

Test all the Python featuers with Pyarmor

    python test_pyfeatures.py

Since Pyarmor 9.3, it only supports HTTPS to reuqest token

For test python without ssl, patch source to use HTTP to request token

    sed -i -e 's?^tokurl.*$?tokurl = http://pyarmor.dashingsoft.com/api/auth2?' pyarmor/cli/default.cfg
