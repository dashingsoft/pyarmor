source test-header.sh
set -e

# ======================================================================
#
# Initial setup.
#
# ======================================================================
PYARMOR="${PYTHON} pyarmor.py"
TESTROOT=$(pwd)
TESTDIR="--testdir ../../lib/test"
TESTLIB=$($PYTHON -c'import sys, test
sys.stdout.write(test.__path__[0])')

ALLENTRIES="test_concurrent_futures.py test_multiprocessing_forkserver.py test_weakref.py"
RUNTIMEFILES="pytransform.py _pytransform.* pyshield.* product.key license.lic"

csih_inform "Python is $PYTHON"
csih_inform "Test package at $TESTLIB"
csih_inform "Tested Package: $pkgfile"
csih_inform "PyArmor is $PYARMOR"

csih_inform "Make workpath ${workpath}"
rm -rf ${workpath}
mkdir -p ${workpath} || csih_error "Make workpath FAILED"

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && cd src/

# From pyarmor 4.5.4, platform name is renamed
# From pyarmor 5.7.5, platform name is changed
csih_inform "Add execute permission to dynamic library"
find ./platforms -name _pytransform.dll -exec chmod +x {} \;

csih_inform "Prepare for python features testing at $(pwd)"
echo ""

csih_inform "Copy $TESTLIB to lib/test"
[[ -d $TESTLIB ]] || csih_error "No test lib found: '$TESTLIB'"
mkdir -p ./lib
cp -a $TESTLIB ./lib

csih_inform "Find test entries"
TESTENTRIES="regrtest.py"
for s in $ALLENTRIES ; do
    [[ -f $TESTLIB/$s ]] && TESTENTRIES="$TESTENTRIES,$s"
done
echo "$TESTENTRIES"

if [[ -z "$TESTDIR" ]] ; then
csih_inform "Move $TESTLIB to ${TESTLIB}.bak"
[[ -d $TESTLIB.bak ]] && csih_error "$TESTLIB.bak has been exists!"
mv $TESTLIB $TESTLIB.bak
fi

# Only for windows and python26, need to convert to unix format
if [[ "$PLATFORM" == win* && "$PYTHON" == *Python26* ]] ; then
  csih_inform "Convert scripts to unix format"
  which dos2unix >/dev/null 2>&1 && \
  for s in $(find ./lib/test -name test_*.py) ; do
    dos2unix $s >>result.log 2>&1
  done
fi

# ======================================================================
#
#  Main: obfuscate all test scripts and run them
#
# ======================================================================

echo ""
echo "-------------------- Start testing ------------------------------"
echo ""

csih_inform "Show help and import pytransform"
$PYARMOR --help >>result.log 2>&1 || csih_error "Bootstrap FAILED"

csih_inform "Create project at projects/pytest"
$PYARMOR init --src=lib/test --entry="$TESTENTRIES" -t pkg projects/pytest >>result.log 2>&1

csih_inform "Change current path to projects/pytest"
cd projects/pytest

csih_inform "Config project to obfuscate all test scripts"
$ARMOR config --manifest="global-include test_*.py, include regrtest.py exclude doctest_*.py" >result.log 2>&1

csih_inform "Obfuscate scripts"
$ARMOR build >>result.log 2>&1

csih_inform "Copy obfuscated scripts to ../../lib/test"
cp -a dist/test/* ../../lib/test/

# Failed Tests:
#
# Python27
#     Hangup: test_argparse.TestFileTypeR* (win32)
#
NOTESTS="test_argparse test_profilehooks test_sys_setprofile test_sys_settrace test_cprofile"

if [[ -z "$TESTDIR" ]] ; then

    csih_inform "Move ../../lib/test to $TESTLIB"
    mv ../../lib/test $TESTLIB

    csih_inform "Run obfuscated test scripts without $NOTESTS"
    # (cd $TESTLIB; $PYTHON regrtest.py -x $NOTESTS) >>result.log 2>&1
    (cd $TESTLIB; $PYTHON regrtest.py -x $NOTESTS)

    csih_inform "Move obfuscated test scripts to ../../lib/test"
    mv $TESTLIB ../../lib/test

    csih_inform "Restore original test scripts"
    mv $TESTLIB.bak $TESTLIB

else

    csih_inform "Run obfuscated test scripts without $NOTESTS"
    ($PYTHON ../../lib/test/regrtest.py $TESTDIR -x $NOTESTS)

fi

# ======================================================================
#
# Finished and cleanup.
#
# ======================================================================
csih_inform "Change current path to test root: ${TESTROOT}"
cd ${TESTROOT}

echo "----------------------------------------------------------------"
echo ""
csih_inform "Test finished for ${PYTHON}"

(( ${_bug_counter} == 0 )) || csih_error "${_bug_counter} bugs found"
echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"
