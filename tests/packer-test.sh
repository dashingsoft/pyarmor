source test-header.sh

# ======================================================================
#
# Initial setup.
#
# ======================================================================

PYTHON=C:/Python34/python
if [[ "$PLATFORM" == "macosx_x86_64" ]] ; then
    PYTHON=python3
fi

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
# From pyarmor 3.5.1, main scripts are in directory "src"
cd src/

csih_inform "Add execute permission to dynamic library"
find ./platforms -name _pytransform.dll -exec chmod +x {} \;

csih_inform "Prepare for packer testing"
echo ""


# ======================================================================
#
#  Bootstrap
#
# ======================================================================

csih_inform "Show help and import pytransform"
$PYARMOR --help >result.log 2>&1 || csih_error "PyArmor bootstrap failed"

# --------------------------------
# Run this testcases only in Win32
# --------------------------------
if [[ "$PLATFORM" == "win32" ]] ; then

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

fi
# --------------------------------
# Run this testcases only in Win32
# --------------------------------

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
( cd $dist/queens; ./queens  >result.log 2>&1 )

check_file_exists $dist/queens/license.lic
check_file_content $dist/queens/result.log 'Found 92 solutions'

rm $dist/queens/license.lic
( cd $dist/queens; ./queens  >result.log 2>&1 )
check_file_content $dist/queens/result.log 'Found 92 solutions' not
check_file_content $dist/queens/result.log 'No such file or directory'

csih_inform "Case 3-2: Test option --name with PyInstaller"
$PYARMOR pack --clean -O dist --name foo2 \
         examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/foo2; ./foo2  >result.log 2>&1 )
check_file_content dist/foo2/result.log 'Found 92 solutions'

csih_inform "Case 3-3: Test one file with PyInstaller"
$PYARMOR pack --clean --name foo3 -O dist --options " --onefile" \
         examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/; ./foo3  >result.log 2>&1 )
check_file_content dist/result.log 'Found 92 solutions'

csih_inform "Case 3-4: Test one file without license by PyInstaller"
cat <<EOF > copy_license.py
import sys
from os.path import join, dirname
with open(join(dirname(sys.executable), 'license.lic'), 'rb') as fs:
    with open(join(sys._MEIPASS, 'license.lic'), 'wb') as fd:
        fd.write(fs.read())
EOF
$PYARMOR pack --clean --without-license --name foo4 -O dist \
         --options " -F --runtime-hook copy_license.py" \
         examples/simple/queens.py >result.log 2>&1
check_return_value

( cd dist/; ./foo4  >result.log 2>&1 )
check_file_content dist/result.log 'Found 92 solutions' not

$PYARMOR licenses test-packer >result.log 2>&1
cp licenses/test-packer/license.lic dist/

( cd dist/; mkdir other; cd other; ../foo4 > ../result.log )
check_return_value
check_file_content dist/result.log 'Found 92 solutions'

csih_inform "Case 3-5: Test module is obfuscated in the bundle"
output=test-module-for-pyinstaller
$PYARMOR pack --debug --output $output examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists main-patched.spec

sed -i -e "s/'exec'/'eval'/g" main-patched.spec >/dev/null 2>&1
$PYTHON -m PyInstaller --clean -y --distpath $output main-patched.spec >result.log 2>&1
check_return_value

(cd $output; ./main/main >result.log 2>&1)
check_file_content $output/result.log "RuntimeError: Check restrict mode failed"

csih_inform "Case 3-6: Test the scripts is obfuscated with restrict mode 2"
dist=test-pyinstaller-restrict-mode
$PYARMOR pack --output $dist -x " --restrict 2" examples/testpkg/main.py >result.log 2>&1
check_return_value

( cd $dist/main; ./main  >result.log 2>&1 )

check_file_exists $dist/main/license.lic
check_file_content $dist/main/result.log 'Hello! PyArmor Test Case'

csih_inform "Case 3-7: Test runtime hook in the src path"
dist=test-runtime-hook
mkdir $dist
echo "print('Test runtime hook OK')" > $dist/test_hook_main.py
echo "print('This is myhook')" > $dist/myhook.py
(cd $dist; $PYTHON ../pyarmor.py pack --output dist -x " --exclude myhook.py" \
         -e " --runtime-hook myhook.py" test_hook_main.py >result.log 2>&1)
check_return_value

( cd $dist; dist/test_hook_main/test_hook_main  >result.log 2>&1 )
check_return_value
check_file_content $dist/result.log 'This is myhook'
check_file_content $dist/result.log 'Test runtime hook OK'

csih_inform "Case 3-8: Test option --with-license"
dist=test-with-license
mkdir $dist
echo "Fake license file" > $dist/fake-license.lic
echo "print('Hello test --with-license')" > $dist/main.py
(cd $dist; $PYTHON ../pyarmor.py pack --output dist \
                   --with-license fake-license.lic main.py >result.log 2>&1)
check_return_value
check_file_exists $dist/dist/main/license.lic

( cd $dist; dist/main/main  >result.log 2>&1 )
check_file_content $dist/result.log 'Hello test --with-license' not
check_file_content $dist/result.log 'Invalid product license file'

csih_inform "Case 3-9: Test pack with project"
project=test-with-project
$PYARMOR init --src examples/simple --entry queens.py $project >result.log 2>&1
check_return_value

$PYARMOR pack -O $project/dist $project >result.log 2>&1
check_return_value
check_file_exists $project/dist/queens/pytransform.key

(cd $project/dist; ./queens/queens >result.log 2>&1)
check_return_value
check_file_content $project/dist/result.log 'Found 92 solutions'

csih_inform "Case 3-10: Test pack with project .json file"
project=test-with-project-file
$PYARMOR init --src examples/simple --entry queens.py $project >result.log 2>&1
check_return_value

mv $project/.pyarmor_config $project/test.json
$PYARMOR pack -O $project/dist $project/test.json >result.log 2>&1
check_return_value
check_file_exists $project/dist/queens/pytransform.key

(cd $project/dist; ./queens/queens >result.log 2>&1)
check_return_value
check_file_content $project/dist/result.log 'Found 92 solutions'

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
