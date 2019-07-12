source test-header.sh

# ======================================================================
#
# Initial setup.
#
# ======================================================================

PYTHON=C:/Python34/python

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

csih_inform "Case 1-1: Test full path entry script with py2exe"
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

csih_inform "Case 2-1: Test full path entry script with cx_Freeze"
$PYARMOR pack --type cx_Freeze examples/cx_Freeze/hello.py >result.log 2>&1
check_return_value

dist=examples/cx_Freeze/build/exe.win32-3.4
( cd $dist; ./hello.exe  >result.log 2>&1 )

check_file_exists $dist/license.lic
check_file_content $dist/result.log 'Found 92 solutions'

echo -e "\n-------------------- cx_Freeze End ---------------------------\n"

# ======================================================================
#
#  Command: pack with PyInstaller
#
# ======================================================================

echo -e "\n------------------ PyInstaller Test ----------------------\n"

csih_inform "Case 3-1: Test full path entry script with PyInstaller"
$PYARMOR pack examples/simple/queens.py >result.log 2>&1
check_return_value

dist=examples/simple/dist
( cd $dist/queens; ./queens.exe  >result.log 2>&1 )

check_file_exists $dist/queens/license.lic
check_file_content $dist/queens/result.log 'Found 92 solutions'

csih_inform "Case 3-2: Test extra pack option with PyInstaller"
$PYARMOR pack --clean --options " --name foo2 " -s "foo2.spec" \
         examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/foo2; ./foo2.exe  >result.log 2>&1 )
check_file_content dist/foo2/result.log 'Found 92 solutions'

csih_inform "Case 3-3: Test one file with PyInstaller"
$PYARMOR pack --clean --options " --name foo3 -F" -s "foo3.spec" \
         examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/; ./foo3.exe  >result.log 2>&1 )
check_file_content dist/result.log 'Found 92 solutions'

csih_inform "Case 3-4: Test one file without license by PyInstaller"
cat <<EOF > copy_license.py
import sys
from os.path import join, dirname
with open(join(dirname(sys.executable), 'license.lic'), 'rb') as fs:
    with open(join(sys._MEIPASS, 'license.lic'), 'wb') as fd:
        fd.write(fs.read())
EOF
$PYARMOR pack --clean --without-license \
         --options " --name foo4 -F --runtime-hook copy_license.py" \
         -s "foo4.spec" examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/; ./foo4.exe  >result.log 2>&1 )
check_file_content dist/result.log 'Found 92 solutions' not

$PYARMOR licenses test-packer >result.log 2>&1
cp licenses/test-packer/license.lic dist/

( cd dist/; mkdir other; cd other; ../foo4.exe > ../result.log )
check_return_value
check_file_content dist/result.log 'Found 92 solutions'

echo -e "\n------------------ PyInstaller End -----------------------\n"

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
