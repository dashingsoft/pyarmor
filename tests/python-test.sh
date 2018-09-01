source test-header.sh

# ======================================================================
#
# Initial setup.
#
# ======================================================================

TESTLIB=${TESTLIB:-C:/Python26/Lib/test}
PYARMOR="${PYTHON} pyarmor2.py"

csih_inform "Python is $PYTHON"
csih_inform "Tested Package: $pkgfile"
csih_inform "Pyarmor is $PYARMOR"

csih_inform "Make workpath ${workpath}"
rm -rf ${workpath}
mkdir -p ${workpath} || csih_error "Make workpath FAILED"

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && mv src/* ./

csih_inform "Prepare for python features testing"
echo ""

csih_inform "Copy $TESTLIB to lib/test"
[[ -d $TESTLIB ]] || csih_error "No test lib found: '$TESTLIB'"
mkdir -p ./lib
cp -a $TESTLIB ./lib

csih_inform "Move $TESTLIB to ${TESTLIB}.bak"
mv $TESTLIB $TESTLIB.bak

csih_inform "Convert scripts to unix format"
which dos2unix >/dev/null 2>&1 && \
for s in $(find ./lib/test -name test_*.py) ; do
  dos2unix $s >>result.log 2>&1
done

# ======================================================================
#
#  Main: obfuscate all test scripts and run them
#
# ======================================================================

echo ""
echo "-------------------- Start testing ------------------------------"
echo ""

csih_inform "Show help and import pytransform"
$PYARMOR --help >>result.log 2>&1 || csih_bug "Bootstrap FAILED"
[[ -f _pytransform$DLLEXT ]] || csih_error "no pytransform extension found"

csih_inform "Create project at 'projects/pytest'"
$PYARMOR init --src=lib/test --entry=regrtest.py projects/pytest >>result.log 2>&1

csih_inform "Change current path to project path"
cd projects/pytest

csih_inform "Config project to obfuscate all test scripts"
$ARMOR config --manifest="global-include test_*.py, exclude doctest_*.py" >result.log 2>&1

csih_inform "Obfuscate scripts"
$ARMOR build >>result.log 2>&1

csih_inform "Copy runtime files to ../../lib/test"
cp dist/* ../../lib/test

csih_inform "Copy entry script to ../../lib/test"
cp dist/test/regrtest.py ../../lib/test

csih_inform "Copy obfuscated scripts to ../../lib/test"
for s in $(find dist/test -name test_*.py) ; do
    cp $s ${s/dist\/test\//..\/..\/lib\/test\/}
done

csih_inform "Move ../../lib/test to $TESTLIB"
mv ../../lib/test $TESTLIB

csih_inform "Run obfuscated test scripts"
(cd $TESTLIB; $PYTHON regrtest.py -x test_profilehooks) >>result.log 2>&1

csih_inform "Move obfuscated test scripts to ../../lib/test"
mv $TESTLIB ../../lib/test

csih_inform "Restore original test scripts"
mv $TESTLIB.bak $TESTLIB

csih_inform "Change current path to pyarmor source path"
cd ../..

# ======================================================================
#
# Finished and cleanup.
#
# ======================================================================

# Return test root
cd ../..

echo "----------------------------------------------------------------"
echo ""
csih_inform "Test finished for ${PYTHON}"

(( ${_bug_counter} == 0 )) || csih_error "${_bug_counter} bugs found"
echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"
