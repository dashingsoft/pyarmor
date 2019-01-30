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
# From pyarmor 3.5.1, main scripts are in directory "src"
cd src/

chmod +x platforms/windows32/_pytransform$DLLEXT
chmod +x platforms/windows64/_pytransform$DLLEXT

csih_inform "Prepare for system testing"
echo ""


# ======================================================================
#
#  Bootstrap
#
# ======================================================================

csih_inform "Show help and import pytransform"
$PYARMOR --help >result.log 2>&1 || csih_error "PyArmor bootstrap failed"

# ======================================================================
#
#  Command: pack with py2exe
#
# ======================================================================

echo -e "\n-------------------- py2exe Test -----------------------------\n"

csih_inform "Case 1-1: Only full path entry script"
$PYARMOR pack --type py2exe examples/py2exe/hello.py >result.log 2>&1
check_return_value

( cd examples/py2exe/dist; ./hello.exe >result.log 2>&1 )

check_file_exists examples/py2exe/dist/license.lic
check_file_content examples/py2exe/dist/result.log 'Found 92 solutions'

echo -e "\n-------------------- py2exe End ------------------------------\n"

# ======================================================================
#
#  Command: pack with cx_Freeze
#
# ======================================================================

echo -e "\n-------------------- cx_Freeze Test --------------------------\n"

csih_inform "Case 2-1: Only full path entry script"
$PYARMOR pack --type cx_Freeze examples/cx_Freeze/hello.py >result.log 2>&1
check_return_value

dist=examples/cx_Freeze/build/exe.win32-3.4
( cd $dist; ./hello.exe  >result.log 2>&1 )

check_file_exists $dist/license.lic
check_file_content $dist/result.log 'Found 92 solutions'

echo -e "\n-------------------- cx_Freeze End ---------------------------\n"

# ======================================================================
#
# Finished and cleanup.
#
# ======================================================================

# Return test root
cd ../../..

echo "----------------------------------------------------------------"
echo ""
csih_inform "Test finished for ${PYTHON}"

(( ${_bug_counter} == 0 )) || csih_error "${_bug_counter} bugs found"
echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"
