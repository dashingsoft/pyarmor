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
[[ -n "$USERPROFILE" ]] && rm -rf "$USERPROFILE\\.pyarmor" "$USERPROFILE\\.pyarmor_capsule.*"

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

csih_inform "Prepare for cross-platform testing"
echo ""


# ======================================================================
#
#  Bootstrap: help and version
#
# ======================================================================

echo ""
echo "-------------------- Bootstrap ---------------------------------"
echo ""

csih_inform "1. show help and import pytransform"
$PYARMOR --help >result.log 2>&1 || csih_bug "Case 1.1 FAILED"

csih_inform "2. show version information"
$PYARMOR --version >result.log 2>&1 || csih_bug "show version FAILED"

echo ""
echo "-------------------- Bootstrap End -----------------------------"
echo ""

# ======================================================================
#
#  Cross Publish
#
# ======================================================================

echo ""
echo "-------------------- Test Cross Publish --------------------"
echo ""

csih_inform "Case CP-1: cross publish by obfuscate"
$PYARMOR obfuscate --platform linux.x86_64 -O test-cross-publish \
         examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_content result.log "linux.x86_64._pytransform.so"

csih_inform "Case CP-2: cross publish by obfuscate with no-cross-protection"
$PYARMOR obfuscate --platform linux.x86_64 -O test-cross-publish \
         --no-cross-protection examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_content result.log "linux.x86_64._pytransform.so"

csih_inform "Case CP-3: cross publish by project"
PROPATH=projects/test-cross-publish
$PYARMOR init --src examples/simple --entry queens.py $PROPATH >result.log 2>&1
$PYARMOR build --platform linux.x86_64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "linux.x86_64._pytransform.so"

csih_inform "Case CP-4: cross publish by project without cross-protection"
$PYARMOR config --cross-protection 0 $PROPATH >result.log 2>&1
check_return_value

$PYARMOR build -B --platform linux.x86_64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "linux.x86_64._pytransform.so"

csih_inform "Case CP-5: cross publish by project with custom cross protection"
$SED -i -e 's/"cross_protection": [01]/"cross_protection": "protect_code.pt"/g' \
    $PROPATH/.pyarmor_config >result.log 2>&1
check_return_value
check_file_content $PROPATH/.pyarmor_config "protect_code.pt"

$PYARMOR build -B --platform linux.x86_64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "linux.x86_64._pytransform.so"

echo ""
echo "-------------------- Test Cross Publish END ------------------------"
echo ""

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
