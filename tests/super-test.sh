# Obfuscate all the test scripts and run them in super mode
source test-header.sh
set -e

PYTHON=${PYTHON:-python3}
PYVER=$($PYTHON -c 'import sys
sys.stdout.write("%s%s" % sys.version_info[:2])')
TESTLIB=$($PYTHON -c'import sys, test
sys.stdout.write(test.__path__[0])')

SRC=$(pwd)/pyarmor-${version}/src
PYARMOR=${PYARMOR:-$PYTHON $SRC/pyarmor.py}

PYARMOR_DATA=~/.pyarmor
[[ -n "$USERPROFILE" ]] && PYARMOR_DATA=$USERPROFILE\\.pyarmor

csih_inform "Python is: $PYTHON"
csih_inform "Python Version $PYVER"
csih_inform "Python test path: $TESTLIB"
csih_inform "PyArmor at: $SRC"
csih_inform "PyArmor data at: ${PYARMOR_DATA}"

[[ ! -d "$SRC" ]] && csih_error "No pyarmor found"

WORKPATH=__runtest3__
csih_inform "Create super mode test workpath: ${WORKPATH}"
rm -rf ${WORKPATH}
mkdir -p ${WORKPATH}
csih_inform "Change to $WORKPATH"
cd ${WORKPATH}

# Name must be "test"
OBFPATH=$(pwd)/test
csih_inform "Copy tests to: $OBFPATH"
cp -a $TESTLIB $OBFPATH
rm -rf $OBFPATH/*.pyc $OBFPATH/*.pyo

csih_inform "Prepare super mode dynamic libraries"
rm -rf ${PYARMOR_DATA}/platforms
mkdir -p ${PYARMOR_DATA}/platforms
PLATFORM_INDEX=${SRC}/platforms/index.json
(cd ${PYARMOR_DATA}/platforms;
 for x in ${PYARMOR_CORE_PLATFORM}/*.py?? ; do
     name=$(basename ${x})
     name=${name//./\/}
     mkdir -p ${name}
     if [[ "${PLATFORM}" == "win_amd64" ]] ; then
         cp ${x}/pytransform.* ${name}
     else
         ln -s ${x}/pytransform.* ${name}
     fi
     update_pytransform_hash256 ${PLATFORM_INDEX} ${x}/pytransform.* $(basename ${x})
 done)

csih_inform "Obfuscate all the test scripts with --advanced 2"
$PYARMOR obfuscate -r --advanced 2 -O $OBFPATH --bootstrap 2 --no-runtime --no-cross-protection \
         --exclude "bad*.py" --exclude encoded_modules --exclude test_descr.py \
         $TESTLIB > obf-result-${PYVER}.log 2>&1

csih_inform "Generate runtime files in the workpath"
$PYARMOR runtime --advanced 2 -O .

csih_inform "Restore non test_*.py"
for x in $(cd $TESTLIB; find . ! -name "test_*.py" | grep "\.py$") ; do
    cp "$TESTLIB/${x:2}" "test/${x:2}"
done

NOTESTS="test_profilehooks test_sys_setprofile test_sys_settrace test_cprofile
         test_inspect test_gdb test_linuxaudiodev test_msilib test_ossaudiodev
         test_sunaudiodev test_winsound test_regrtest test_runpy test_dis
         test_code test_compile test_compileall"

csih_inform "Removing no test scritps ..."
for x in $NOTESTS ${PY27_NOTESTS} ${PY37_NOTESTS} ${PY38_NOTESTS} ; do
    csih_inform "Remove script: $x.py"
    rm -rf ${OBFPATH}/$x.py
done

# csih_inform "Run normal test scripts, save baseline to baseline-${PYVER}.log"
# $PYTHON -E -m test > baseline-${PYVER}.log 2>&1

csih_inform "Run all the obfuscated test scripts"
$PYTHON -E -m test > result-${PYVER}.log 2>&1
