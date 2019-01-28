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

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && mv src/* ./

# From pyarmor 4.5.4, platform name is renamed
if [[ -d platforms/windows32 ]] ; then
    csih_inform "Add execute permission to dynamic library"
    chmod +x platforms/windows32/_pytransform.dll
    chmod +x platforms/windows64/_pytransform.dll
fi

csih_inform "Prepare for function testing"
echo ""

# ======================================================================
#
# Start test.
#
# ======================================================================

csih_inform "1. Show version information"
$PYARMOR --version >result.log 2>&1 || csih_bug "show version FAILED"

csih_inform "2. Obfuscate foo.py"
$PYARMOR obfuscate examples/helloworld/foo.py >result.log 2>&1
check_return_value

csih_inform "3. Run obfuscated foo.py"
(cd dist; $PYTHON foo.py >result.log 2>&1)
check_return_value
check_file_content dist/result.log "This license for PyArmor-Project is never expired"
check_file_content dist/result.log "Hello world"
check_file_content dist/result.log "1 + 1 = 2"

csih_inform "4. Generate expired license"
$PYARMOR licenses -e $(next_month) Joker >result.log 2>&1
check_return_value
check_file_exists licenses/Joker/license.lic

csih_inform "3. Run obfuscated foo.py with expired license"
cp licenses/Joker/license.lic dist/
(cd dist; $PYTHON foo.py >result.log 2>&1)
check_return_value
check_file_content dist/result.log "This license for Joker will be expired in"
check_file_content dist/result.log "Hello world"
check_file_content dist/result.log "1 + 1 = 2"

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
