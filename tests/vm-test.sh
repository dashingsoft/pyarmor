set -x
set -e

PLATFORMS=$(pwd)/../../pyarmor-core/platforms
TESTPATH=__runtest4__
DIST="$(pwd)/../dist"
for x in $(cd ${DIST}; ls -t pyarmor-*.tar.gz) ; do
    pkgfile=${DIST}/$x
    break
done
[[ -z "$pkgfile" ]] && echo "No pyarmor package found" && exit

rm -rf $TESTPATH
mkdir -p $TESTPATH/.pyarmor

pkgname=$(cd $TESTPATH; tar xzf ${pkgfile}; ls -d pyarmor-*)
find $TESTPATH -name "*.dll" -exec chmod +x {} \;

if [[ $(uname) == CYGWIN* ]] ; then
    TESTHOME=$(cygpath -m $(pwd)/$TESTPATH/.pyarmor)
    TESTSRC=$(cygpath -m $(pwd)/$TESTPATH/$pkgname/src)
else
    TESTHOME=$TESTPATH/.pyarmor
    TESTSRC=$(pwd)/$TESTPATH/$pkgname/src
fi
TESTSCRIPT=$TESTSRC/examples/simple/queens.py
[[ ! -d "$TESTSRC" ]] && echo "No pyarmor found" && exit

cd $TESTPATH
for x in x86 x86_64 ; do
    mkdir -p .pyarmor/platforms/windows/$x/21
    cp ${PLATFORMS}/windows.$x.21/_pytransform.dll .pyarmor/platforms/windows/$x/21
    for y in py27 py37 py38 ; do
        mkdir -p .pyarmor/platforms/windows/$x/25/$y
        cp ${PLATFORMS}/windows.$x.25.$y/pytransform.pyd .pyarmor/platforms/windows/$x/25/$y
    done
done

TEST_VERSIONS="27 37 38 27-32 37-32 38-32"

for pyver in ${TEST_VERSIONS} ; do
    PYTHON="C:/Python${pyver}/python"
    PYARMOR="$PYTHON $TESTSRC/pyarmor.py --home $TESTHOME -d"

    DIST=dist3-${pyver}
    $PYARMOR obfuscate --advanced 3 -O $DIST $TESTSCRIPT
    (cd $DIST; $PYTHON $(basename $TESTSCRIPT) >result.log 2>&1)

    DIST=dist4-${pyver}
    $PYARMOR obfuscate --advanced 4 -O $DIST $TESTSCRIPT
    (cd $DIST; $PYTHON $(basename $TESTSCRIPT) >result.log 2>&1)
done

for x in $(find . -name result.log) ; do
    grep -q "Found 92 solutions" $x || echo "Failed: $x"
done
