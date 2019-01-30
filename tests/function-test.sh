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

[[ -d data ]] || csih_error "No path 'data' found in current path"
datapath=$(pwd)/data

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

csih_inform "Make path test/data"
mkdir -p test/data
csih_inform "Copy test files from ${datapath} to ./test/data"
cp ${datapath}/*.py test/data
cp ${datapath}/project.zip test/data

csih_inform "Prepare for function testing"
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
#  Command: init, config, licenses, obfuscate
#
# ======================================================================

echo ""
echo "-------------------- Command ---------------------------------"
echo ""

csih_inform "C-1. Test option --capsule for init"
$PYARMOR init --src=examples/simple --capsule=test/data/project.zip \
    projects/test-capsule >result.log 2>&1
check_return_value
check_file_content projects/test-capsule/.pyarmor_config "project.zip"

csih_inform "C-2. Test option --capsule for config"
cp test/data/project.zip projects/test-capsule/project2.zip
$PYARMOR config --capsule=project2.zip projects/test-capsule >result.log 2>&1

check_return_value
check_file_content projects/test-capsule/.pyarmor_config "project2.zip"

csih_inform "C-3. Test option --capsule for obfuscate"
$PYARMOR init --src=examples/simple test-capsule >result.log 2>&1
$PYARMOR obfuscate --src=examples/simple --output=dist-capsule \
    --entry=queens.py --capsule=test-capsule/.pyarmor-capsule.zip \
    >result.log 2>&1

check_file_exists dist-capsule/queens.py
check_file_content dist-capsule/queens.py '__pyarmor__(__name__'

(cd dist-capsule; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content dist-capsule/result.log 'Found 92 solutions'

csih_inform "C-4. Test command licenses"

cp test/data/project.zip .pyarmor_capsule.zip
$PYARMOR licenses --expired=2018-05-12 Customer-Jordan >result.log 2>&1
check_file_exists licenses/Customer-Jordan/license.lic

$PYARMOR licenses --capsule=test/data/project.zip --output=projects \
    --expired=2018-05-12 Customer-Jordan >result.log 2>&1
check_file_exists projects/licenses/Customer-Jordan/license.lic

$PYARMOR init --src=examples/simple --entry=queens.py \
    projects/test-licenses >result.log 2>&1
$PYARMOR licenses --project=projects/test-licenses \
    --expired=2018-05-12 Customer-Jordan >result.log 2>&1
check_file_exists projects/test-licenses/licenses/Customer-Jordan/license.lic

$PYARMOR licenses --project=projects/test-licenses \
    -e 2018-05-12 --bind-disk '100304PBN2081SF3NJ5T' \
    Customer-Tom >result.log 2>&1

$PYARMOR licenses --project=projects/test-licenses \
    -e 2018-05-12 Customer-A Customer-B Customer-C >result.log 2>&1
check_file_exists projects/test-licenses/licenses/Customer-A/license.lic
check_file_exists projects/test-licenses/licenses/Customer-B/license.lic
check_file_exists projects/test-licenses/licenses/Customer-C/license.lic

csih_inform "C-5. Test option --bind-file for licenses"
$PYARMOR init --src=examples/simple --entry queens.py \
    projects/test-bind-file >result.log 2>&1
check_return_value

cat <<EOF > projects/test-bind-file/id_rsa
-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----
EOF

(cd projects/test-bind-file && $ARMOR build >result.log 2>&1 &&
  $ARMOR licenses --bind-file="id_rsa;id_rsa" \
      TESTER >result.log 2>&1 &&
  cd dist && cp ../id_rsa ./ &&
  cp ../licenses/TESTER/license.lic ./ &&
  $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content projects/test-bind-file/dist/result.log 'Found 92 solutions'

csih_inform "C-6. Test option --recursive for obfuscate"
rm .pyarmor_capsule.zip
$PYARMOR obfuscate --src=examples/simple --entry queens.py --recursive \
    -O dist-recursive >result.log 2>&1
check_return_value

(cd dist-recursive; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content dist-recursive/result.log 'Found 92 solutions'

csih_inform "C-7. Test no entry script for obfuscate"
$PYARMOR obfuscate --src=examples/simple -O test-no-entry >result.log 2>&1
check_return_value
check_file_exists test-no-entry/queens.py

csih_inform "C-8. Test 'gbk' codec for obfuscate"

if [[ "$PYTHON" == C:/Python30/python || "$PYTHON" == *python3.0 ||
      ( "$PLATFORM" == "macosx_x86_64" && "$PYTHON" == *python2.7 ) ]] ; then
csih_inform "This testcase is ignored in Python 3.0, and Python2 in MacOS"
else
mkdir -p test-codec
cp $datapath/gbk.py test-codec
$PYARMOR obfuscate -O dist-codec test-codec/gbk.py >result.log 2>&1
check_return_value
check_file_exists dist-codec/gbk.py

(cd dist-codec; $PYTHON gbk.py >result.log 2>&1 )
check_return_value
check_file_content dist-codec/result.log 'PyArmor'
fi

echo ""
echo "-------------------- Command End -----------------------------"
echo ""

# ======================================================================
#
#  Mode: auto-wrap
#
# ======================================================================

echo ""
echo "-------------------- Test Mode auto-wrap --------------------"
echo ""

csih_inform "Case F-1: run obfuscated scripts with auto-wrap mode"

for mod_mode in none des ; do

csih_inform "Test obf-module-mode is ${mod_mode} ..."
PROPATH=projects/testmod_auto_wrap
$PYARMOR init --src=test/data --entry=wrapcase.py $PROPATH >result.log 2>&1
$PYARMOR config --obf-module-mode=${mod_mode} \
                --obf-code-mode=wrap --disable-restrict-mode=1 \
                --manifest="include wrapcase.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_return_value
check_file_exists $PROPATH/dist/wrapcase.py
check_file_content $PROPATH/dist/wrapcase.py 'pyarmor_runtime'
check_file_content $PROPATH/dist/wrapcase.py '__pyarmor__(__name__'

(cd $PROPATH/dist; $PYTHON wrapcase.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'recursive call return solved'
check_file_content $PROPATH/dist/result.log 'auto wrap mode exception'
check_file_content $PROPATH/dist/result.log 'second test decorator return OK'

csih_inform "Test obf-module-mode is ${mod_mode} END"
done


echo ""
echo "-------------------- Test Mode auto-wrap END ------------------------"
echo ""

# ======================================================================
#
#  Test Feture: __spec__ and multiprocessing
#
# ======================================================================

echo ""
echo "-------------------- Test Feature: __spec__ --------------------"
echo ""

if [[ "$PLATFORM" == win[3_]* && "$PYTHON" == C:/Python3[012]/python ]] ; then

csih_inform "This testcase is ignored in this platform"

else

csih_inform "Case M-1: run obfuscated scripts with multiprocessing 1"

PROPATH=projects/test_spec
$PYARMOR init --src=test/data --entry=mp.py $PROPATH >result.log 2>&1
$PYARMOR config --manifest="include mp.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_return_value
check_file_exists $PROPATH/dist/mp.py
check_file_content $PROPATH/dist/mp.py 'pyarmor_runtime'
check_file_content $PROPATH/dist/mp.py '__pyarmor__(__name__'

(cd $PROPATH/dist; $PYTHON mp.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'module name: __main__'
check_file_content $PROPATH/dist/result.log 'function f'
check_file_content $PROPATH/dist/result.log 'hello bob'
check_file_content $PROPATH/dist/result.log 'main line'

csih_inform "Case M-1: run obfuscated scripts with multiprocessing 2"

# sed -i -e "1,2 d" $PROPATH/dist/mp.py

cat <<EOF >> $PROPATH/dist/main.py
from pytransform import pyarmor_runtime
pyarmor_runtime()

import mp
mp.main()
EOF

(cd $PROPATH/dist; $PYTHON mp.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'module name: __main__'
check_file_content $PROPATH/dist/result.log 'function f'
check_file_content $PROPATH/dist/result.log 'hello bob'
check_file_content $PROPATH/dist/result.log 'main line'

fi

echo ""
echo "-------------------- Test Feature: __spec__ END ----------------"
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
