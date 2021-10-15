# Obfuscate the test scripts and run them in super-plus mode
source test-header.sh
set -e

SCRIPT=test-sppmode.py
PYTHON=${PYTHON:-python3}
PYVER=$($PYTHON -c 'import sys
sys.stdout.write("%s%s" % sys.version_info[:2])')

SRC=$(pwd)/pyarmor-${version}/src
[[ $(uname) == CYGWIN* ]] && SRC=$(cygpath -m $SRC)
PYARMOR=${PYARMOR:-$PYTHON $SRC/pyarmor.py}

PYARMOR_DATA=~/.pyarmor
[[ "$PYVER" == "38" ]] && [[ -n "$USERPROFILE" ]] && PYARMOR_DATA=$USERPROFILE\\.pyarmor

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
cp ${SCRIPT} ${WORKPATH}
csih_inform "Change to $WORKPATH"
cd ${WORKPATH}

csih_inform "Prepare super mode dynamic libraries"
rm -rf ${PYARMOR_DATA}/platforms
mkdir -p ${PYARMOR_DATA}/platforms

PLATFORM_INDEX=${PYARMOR_DATA}/platforms/index.json
cp ${PYARMOR_CORE_PLATFORM}/index.json ${PLATFORM_INDEX}

(cd ${PYARMOR_DATA}/platforms;
 for x in ${PYARMOR_CORE_PLATFORM}/*.py?? ; do
     name=$(basename ${x})
     name=${name//./\/}
     mkdir -p ${name}
     if [[ "${PLATFORM}" == "win_amd64" ]] ; then
         for y in ${x}/pytransform.* ; do
             [[ -f "${y}" ]] && cp ${y} ${name}
         done
     else
         ln -s ${x}/pytransform.* ${name}
     fi
     update_pytransform_hash256 ${PLATFORM_INDEX} ${x}/pytransform.* $(basename ${x})
 done)

OBFPATH=sppdist

csih_inform "Obfuscate the test script with --advanced 5"
$PYARMOR obfuscate --advanced 5 -O $OBFPATH --exact $SCRIPT > obf-result-${PYVER}.log 2>&1

csih_inform "Run the obfuscated test script: $SCRIPT"
$PYTHON $OBFPATH/$SCRIPT > result-${PYVER}.log 2>&1
