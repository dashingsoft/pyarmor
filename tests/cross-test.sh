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
clear_pyarmor_installed_data

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
#  Generate runtime package with different platform
#
# ======================================================================

echo ""
echo "-------------------- Test Cross Runtime --------------------"
echo ""

OUTPUT=./dist

csih_inform "Case CR-1: cross runtime with one platform windows.x86"
rm -rf $OUTPUT
$PYARMOR runtime --platform windows.x86 >result.log 2>&1
check_return_value
check_file_content result.log "windows/x86/_pytransform.dll"
check_file_exists $OUTPUT/pytransform/_pytransform.dll

csih_inform "Case CR-2: cross runtime with one platform alpine.x86_64"
rm -rf $OUTPUT
$PYARMOR runtime --platform alpine.x86_64 >result.log 2>&1
check_return_value
check_file_content result.log "alpine/x86_64/0/_pytransform.so"
check_file_exists $OUTPUT/pytransform/_pytransform.so

csih_inform "Case CR-3: cross runtime with one platform linux.armv7"
rm -rf $OUTPUT
$PYARMOR runtime --platform linux.armv7 >result.log 2>&1
check_return_value
check_file_content result.log "linux/armv7/3/_pytransform.so"
check_file_exists $OUTPUT/pytransform/_pytransform.so

csih_inform "Case CR-4: cross runtime with multi-platforms linux.armv7,linux.aarch32"
rm -rf $OUTPUT
$PYARMOR runtime --platform linux.armv7,linux.aarch32 >result.log 2>&1
check_return_value
check_file_content result.log "linux/armv7/3/_pytransform.so"
check_file_content result.log "linux/aarch32/3/_pytransform.so"
check_file_exists $OUTPUT/pytransform/platforms/linux/armv7/_pytransform.so
check_file_exists $OUTPUT/pytransform/platforms/linux/aarch32/_pytransform.so

csih_inform "Case CR-5: cross runtime with multi-platforms linux.x86_64,darwin.x86_64,linux.aarch64"
rm -rf $OUTPUT
$PYARMOR runtime --platform linux.x86_64,darwin.x86_64,linux.aarch64 >result.log 2>&1
check_return_value
check_file_content result.log "linux/x86_64/_pytransform.so"
check_file_content result.log "darwin/x86_64/_pytransform.dylib"
check_file_content result.log "linux/aarch64/3/_pytransform.so"
check_file_exists $OUTPUT/pytransform/platforms/linux/x86_64/_pytransform.so
check_file_exists $OUTPUT/pytransform/platforms/darwin/x86_64/_pytransform.dylib
check_file_exists $OUTPUT/pytransform/platforms/linux/aarch64/_pytransform.so

csih_inform "Case CR-6: cross runtime with multi-platforms linux.arm,windows.x86_64"
rm -rf $OUTPUT
$PYARMOR runtime --platform linux.arm,windows.x86_64 >result.log 2>&1
check_return_value
check_file_content result.log "linux/arm/0/_pytransform.so"
check_file_content result.log "windows/x86_64/0/_pytransform.dll"
check_file_exists $OUTPUT/pytransform/platforms/linux/arm/_pytransform.so
check_file_exists $OUTPUT/pytransform/platforms/windows/x86_64/_pytransform.dll

csih_inform "Case CR-7: cross runtime with multi-platforms windows.x86,linux.x86_64,linux.arm"
rm -rf $OUTPUT
$PYARMOR runtime --platform windows.x86,linux.x86_64,linux.arm >result.log 2>&1
check_file_content result.log "No dynamic library found for linux.arm with features"

echo ""
echo "-------------------- Test Cross Runtime END ------------------------"
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
&& clear_pyarmor_installed_data \
&& csih_inform "Congratulations, there is no bug found"
