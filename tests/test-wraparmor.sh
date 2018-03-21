# This script is used to test performance of decorator wraparmor
#
# Usage:
#
#    bash test-wraparmor.sh
#
VERSION=$1
if [[ "$VERSION" == "" ]] ; then
    echo "Usage:"
    echo "  bash test-wraparmor.sh VERSION"
    exit 1
fi

PYTHON=C:/Python27/python
test -f $PYTHON || PYTHON=python

WORKPATH=__test_wrapper__
PYARMOR="$PYTHON $WORKPATH/pyarmor-${VERSION}/src/pyarmor.py"
SCRIPT=a.py
SCRIPT_OBF=b.py

mkdir -p $WORKPATH
(cd $WORKPATH; unzip ../../dist/pyarmor-${VERSION}.zip > /dev/null)

# Change n to change total size of function body
let -i n=100
REPEAT_CODE_HOLDER="i += 1"
while (( n )) ; do
    REPEAT_CODE_HOLDER=$(echo -e "${REPEAT_CODE_HOLDER}\n        i += 1")
    let n=n-1
done

REPEAT_CALL_TIMES=1000

cat <<EOF > $WORKPATH/${SCRIPT}

def foo():
    if 0:
        i = 0
        ${REPEAT_CODE_HOLDER}

def main():
    for i in range(${REPEAT_CALL_TIMES}):
        foo()

if __name__ == '__main__':
    import time
    t1 = time.clock()
    main()
    t2 = time.clock()
    print ("Elapse time: %fms" % ((t2 - t1) * 1000))

EOF

cat <<EOF > $WORKPATH/${SCRIPT_OBF}

try:
    from builtins import __wraparmor__
except Exception:
   from __builtin__ import __wraparmor__

def wraparmor(func):
    func.__refcalls__ = 0
    def wrapper(*args, **kwargs):
        __wraparmor__(func)
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise err
        finally:
            __wraparmor__(func, 1)
    wrapper.__module__ = func.__module__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__.update(func.__dict__)
    return wrapper

@wraparmor
def foo():
    if 0:
        i = 0
        ${REPEAT_CODE_HOLDER}

@wraparmor
def main():
    for i in range(${REPEAT_CALL_TIMES}):
        foo()

if __name__ == '__main__':
    import time
    t1 = time.clock()
    main()
    t2 = time.clock()
    print ("Elapse time: %fms" % ((t2 - t1) * 1000))

EOF

#
# Obfuscate script
#
$PYARMOR obfuscate --src $WORKPATH --entry ${SCRIPT_OBF} --output=$WORKPATH/dist ${SCRIPT_OBF}

echo "------------------------------"
echo Run obfuscated script ${SCRIPT_OBF} with decorator
(cd $WORKPATH/dist; $PYTHON ${SCRIPT_OBF})

#
# Get baseline
#
echo "------------------------------"
echo Run normal script ${SCRIPT}
$PYTHON $WORKPATH/${SCRIPT}


# Clean workpath
rm -rf ${WORKPATH}
