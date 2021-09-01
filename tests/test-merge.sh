source test-header.sh

# ======================================================================
#
# Initial setup.
#
# ======================================================================

PYARMOR="${PYTHON} pyarmor.py"

csih_inform "Python is $PYTHON"
csih_inform "Tested Package: $pkgfile"
csih_inform "PyArmor is $PYARMOR"

csih_inform "Make workpath ${workpath}"
rm -rf ${workpath}
mkdir -p ${workpath} || csih_error "Make workpath FAILED"

csih_inform "Clean pyarmor data"
rm -rf  ~/.pyarmor ~/.pyarmor_capsule.*
PYARMOR_DATA=~/.pyarmor
if [[ "${PLATFORM}" == "win_amd64" && "${PYTHON}" == *Python38*/python ]] ; then
    [[ -n "$USERPROFILE" ]] && rm -rf "$USERPROFILE\\.pyarmor*" \
        && PYARMOR_DATA=$USERPROFILE\\.pyarmor
fi
csih_inform "PyArmor data at ${PYARMOR_DATA}"

[[ -d data ]] || csih_error "No path 'data' found in current path"
datapath=$(pwd)/data

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && mv src/* ./

# Fix issue: assert_builtin(open) fails in python 3.0
patch_cross_protection_code_for_python3.0

# From pyarmor 4.5.4, platform name is renamed
# From pyarmor 5.7.5, platform name is changed
csih_inform "Add execute permission to dynamic library"
find ./platforms -name _pytransform.dll -exec chmod +x {} \;

csih_inform "Make path test/data"
mkdir -p test/data
csih_inform "Copy test files from ${datapath} to ./test/data"
cp ${datapath}/*.py test/data
cp -a ${datapath}/sound test/data
cp ${datapath}/project.zip test/data
cp ${datapath}/project.zip test/data/project-orig.zip

if [[ "${PLATFORM}" != "win32" ]] ; then
csih_inform "Make link to platforms for super mode"
if [[ "OK" == $($PYTHON -c'from sys import version_info as ver, stdout
stdout.write("OK" if (ver[0] * 10 + ver[1]) in (27, 37, 38, 39) else "")') ]] ; then
SUPERMODE=yes
mkdir -p ${PYARMOR_DATA}/platforms
PLATFORM_INDEX=${PYARMOR_DATA}/platforms/index.json
if ! [[ -f ${PLATFORM_INDEX} ]] ; then
    csih_inform "Copy platform index.json from pyarmor-core"
    cp ../../../../pyarmor-core/platforms/index.json ${PLATFORM_INDEX}
fi
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
fi
csih_inform "Super mode test is ${SUPERMODE}"
fi

csih_inform "Prepare to test merge feature"
echo ""
echo "-------------------- Merge Test -------------------------------"

# ======================================================================
#
#  Merge feature
#
# ======================================================================

if [[ -f "/home/jondy/workspace/pyarmor/tests/local-py1" ]] ; then
    PYTHON1="/home/jondy/workspace/pyarmor/tests/local-py1"
else
    PYTHON1="python"
fi
if [[ -f "/home/jondy/workspace/pyarmor/tests/local-py2" ]] ; then
    PYTHON2="/home/jondy/workspace/pyarmor/tests/local-py2"
else
    PYTHON2="python3"
fi

PYARMOR1="${PYTHON1} pyarmor.py"
PYARMOR2="${PYTHON2} pyarmor.py"

$PYARMOR --help >result.log 2>&1 || csih_bug "Case 1.1 FAILED"

csih_inform "1 Merge for non super mode"
dist=merged_dist
$PYARMOR1 obfuscate -O dist1 examples/simple/queens.py >result.log 2>&1
$PYARMOR2 obfuscate -O dist2 examples/simple/queens.py >result.log 2>&1
${PYTHON} helper/merge.py -O $dist dist1 dist2 >result.log 2>&1

csih_inform "run merged script by $PYTHON1"
(cd $dist; $PYTHON1 queens.py >result1.log 2>&1)
check_return_value
check_file_content $dist/result1.log 'Found 92 solutions'

csih_inform "run merged script by $PYTHON2"
(cd $dist; $PYTHON2 queens.py >result2.log 2>&1)
check_return_value
check_file_content $dist/result2.log 'Found 92 solutions'


if [[ "yes" == "${SUPERMODE}" ]] ; then

csih_inform "2. Merge for super mode"
dist=merged_super_dist
$PYARMOR1 obfuscate --advanced 2 -O super_dist1 \
    examples/simple/queens.py >result.log 2>&1
$PYARMOR2 obfuscate --advanced 2 -O super_dist2 \
    examples/simple/queens.py >result.log 2>&1
${PYTHON} helper/merge.py -O $dist \
          super_dist1 super_dist2 >result.log 2>&1

csih_inform "run merged script by $PYTHON1"
(cd $dist; $PYTHON1 queens.py >result1.log 2>&1)
check_return_value
check_file_content $dist/result1.log 'Found 92 solutions'

csih_inform "run merged script by $PYTHON2"
(cd $dist; $PYTHON2 queens.py >result2.log 2>&1)
check_return_value
check_file_content $dist/result2.log 'Found 92 solutions'

fi

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

echo           "" \
&& csih_inform "Remove workpath ${workpath}" \
&& echo        "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"
