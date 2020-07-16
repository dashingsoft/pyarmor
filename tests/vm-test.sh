set -x
set -e

TESTPATH=__runtest4__

if [[ $(uname) == CYGWIN* ]] ; then
    TESTHOME=$(cygpath -m $(pwd)/$TESTPATH/.pyarmor)
    TESTSRC=$(cygpath -m $(pwd)/pyarmor/src)
else
    TESTHOME=$TESTPATH/.pyarmor
    TESTSRC=$(pwd)/pyarmor/src
fi
TESTSCRIPT=$TESTSRC/examples/simple/queens.py

[[ ! -d "$TESTSRC" ]] && echo "No pyarmor found" && exit

rm -rf $TESTPATH
mkdir -p $TESTPATH/.pyarmor
cd $TESTPATH

TEST_VERSIONS="27 37 38 27-32 37-32 38-32"

for pyver in ${TEST_VERSIONS} ; do
    PYTHON="C:/Python${pyver}/python"
    PYARMOR="$PYTHON $TESTSRC/pyarmor.py --home $TESTHOME"

    DIST=dist3-${pyver}
    PYARMOR_HOME=$TESTHOME $PYARMOR obfuscate --advanced 3 -O $DIST $TESTSCRIPT
    (cd $DIST; $PYTHON $(basename $TESTSCRIPT) >result.log 2>&1)

    DIST=dist4-${pyver}
    PYARMOR_HOME=$TESTHOME $PYARMOR obfuscate --advanced 4 -O $DIST $TESTSCRIPT
    (cd $DIST; $PYTHON $(basename $TESTSCRIPT) >result.log 2>&1)
done
