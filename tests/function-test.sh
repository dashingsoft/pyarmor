source test-header.sh

# ======================================================================
#
# Initial setup.
#
# ======================================================================

PYARMOR="${PYTHON} pyarmor.py"

csih_inform "Python is $PYTHON"
csih_inform "Tested Package: $pkgfile"
csih_inform "Pyarmor is $PYARMOR"

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
[[ -f _pytransform$DLLEXT ]] || csih_error "no pytransform extension found"

csih_inform "2. show version information"
$PYARMOR --version >result.log 2>&1 || csih_bug "show version FAILED"

echo ""
echo "-------------------- Bootstrap End -----------------------------"
echo ""


# ======================================================================
#
#  Command: init and config
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

$PYARMOR licenses --capsule=test/data/project.zip \
    --disable-restrict-mode --output=projects \
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
