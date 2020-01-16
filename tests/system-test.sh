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

csih_inform "Prepare for system testing"
echo ""


# ======================================================================
#
#  Bootstrap: help and version
#
# ======================================================================

echo ""
echo "-------------------- Bootstrap ---------------------------------"
echo ""

csih_inform "Case 0.1: show help and import pytransform"
$PYARMOR --help >result.log 2>&1 || csih_bug "Case 0.1 FAILED"

csih_inform "Case 0.2: show version information"
$PYARMOR --version >result.log 2>&1 || csih_bug "show version FAILED"

echo ""
echo "-------------------- Bootstrap End -----------------------------"
echo ""

# ======================================================================
#
#  Command: obfuscate
#
# ======================================================================

echo ""
echo "-------------------- Test Command obfuscate --------------------"
echo ""

csih_inform "Case 1.1: obfuscate script"
$PYARMOR obfuscate --output dist examples/simple/queens.py >result.log 2>&1

check_file_exists dist/queens.py
check_file_content dist/queens.py '__pyarmor__(__name__'

( cd dist; $PYTHON queens.py >result.log 2>&1 )
check_file_content dist/result.log 'Found 92 solutions'

csih_inform "Case 1.2-1: obfuscate script with --recursive and --restrict=0"
$PYARMOR obfuscate --recursive --restrict=0 --output dist2 \
                    examples/py2exe/hello.py >result.log 2>&1

check_return_value
check_file_exists dist2/hello.py
check_file_content dist2/hello.py 'pyarmor_runtime()'
check_file_exists dist2/queens.py
check_file_content dist2/queens.py '__pyarmor__(__name__'
check_file_exists dist2/pytransform/__init__.py
check_file_exists dist2/pytransform/license.lic
check_file_not_exists dist2/license.lic

( cd dist2; $PYTHON hello.py >result.log 2>&1 )
check_return_value
check_file_content dist2/result.log 'Found 92 solutions'

csih_inform "Case 1.2-2: obfuscate script with --recursive and --restrict=1"
$PYARMOR obfuscate --recursive --restrict=1 --output dist2-2 \
                    examples/py2exe/hello.py >result.log 2>&1

check_return_value
check_file_exists dist2-2/hello.py
check_file_content dist2-2/hello.py 'pyarmor_runtime()'
check_file_exists dist2-2/queens.py
check_file_content dist2-2/queens.py '__pyarmor__(__name__'

( cd dist2-2; $PYTHON hello.py >result.log 2>&1 )
check_return_value
check_file_content dist2-2/result.log 'Found 92 solutions'

csih_inform "Case 1.2-3: obfuscate script with --package-runtime=0 and --restrict=0"
$PYARMOR obfuscate --package-runtime=0 --restrict=0 --output dist2-3 \
                   -r examples/py2exe/hello.py >result.log 2>&1

check_return_value
check_file_exists dist2-3/hello.py
check_file_content dist2-3/hello.py 'pyarmor_runtime()'
check_file_exists dist2-3/pytransform.py

( cd dist2-3; $PYTHON hello.py >result.log 2>&1 )
check_return_value
check_file_content dist2-3/result.log 'Found 92 solutions'

csih_inform "Case 1.3: run obfuscate script with new license"
$PYARMOR obfuscate --output dist3 examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_exists dist3/queens.py

$PYARMOR licenses --expired $(next_month) Jondy >result.log 2>&1
check_return_value
check_file_exists licenses/Jondy/license.lic
cp licenses/Jondy/license.lic dist3/pytransform/

( cd dist3; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content dist3/result.log 'Found 92 solutions'

csih_inform "Case 1.4: obfuscate one script exactly without runtime files"
$PYARMOR obfuscate --output dist4 --exact --no-runtime \
         examples/pybench/pybench.py >result.log 2>&1
check_return_value
check_file_exists dist4/pybench.py
check_file_not_exists dist4/Lists.py
check_file_not_exists dist4/pytransform.py
check_file_not_exists dist4/pytransform/__init__.py

echo ""
echo "-------------------- Test Command obfuscate END ----------------"
echo ""


# ======================================================================
#
#  Command: init
#
# ======================================================================

echo ""
echo "-------------------- Test Command init -------------------------"
echo ""

csih_inform "Case 2.1: init pybench"
$PYARMOR init --type=app --src examples/pybench --entry pybench.py \
              projects/pybench >result.log 2>&1

check_file_exists projects/pybench/.pyarmor_config

csih_inform "Case 2.1: init py2exe"
$PYARMOR init --src examples/py2exe --entry "hello.py,setup.py" \
              projects/py2exe >result.log 2>&1

check_file_exists projects/py2exe/.pyarmor_config

# csih_inform "Case 2.2: init clone py2exe"
# $PYARMOR init --src examples/py2exe2 --clone projects/py2exe \
#               projects/py2exe-clone >result.log 2>&1
#
# check_return_value
# check_file_exists projects/py2exe-clone/.pyarmor_config

csih_inform "Case 2.3: init package"
$PYARMOR init --src examples/testpkg/mypkg --entry "../main.py" \
              projects/testpkg >result.log 2>&1

check_return_value

$PYARMOR config --disable-restrict-mode=1 projects/testpkg >result.log 2>&1
$PYARMOR info projects/testpkg >result.log 2>&1

check_return_value
check_file_content result.log 'restrict_mode: 0'
check_file_content result.log 'is_package: 1'

echo ""
echo "-------------------- Test Command init END ---------------------"
echo ""

# ======================================================================
#
#  Command: config
#
# ======================================================================

echo ""
echo "-------------------- Test Command config -----------------------"
echo ""

csih_inform "Case 3.1: config py2exe"
( cd projects/py2exe; $ARMOR config --runtime-path='' \
    --manifest="global-include *.py, exclude __manifest__.py" \
    >result.log 2>&1 )
check_return_value

csih_inform "Case 3.2: config pybench"
( cd projects/pybench; $ARMOR config --disable-restrict-mode=1 \
    >result.log 2>&1 )
check_return_value

echo ""
echo "-------------------- Test Command config END -------------------"
echo ""

# ======================================================================
#
#  Command: info
#
# ======================================================================

echo ""
echo "-------------------- Test Command info -------------------------"
echo ""

csih_inform "Case 4.1: info pybench"
( cd projects/pybench; $ARMOR info >result.log 2>&1 )
check_return_value

csih_inform "Case 4.2: info py2exe"
( cd projects/py2exe; $ARMOR info >result.log 2>&1 )
check_return_value

echo ""
echo "-------------------- Test Command info END ---------------------"
echo ""

# ======================================================================
#
#  Command: check
#
# ======================================================================

echo ""
echo "-------------------- Test Command check ------------------------"
echo ""

csih_inform "Case 5.1: check pybench"
( cd projects/pybench; $ARMOR check >result.log 2>&1 )
check_return_value

csih_inform "Case 5.2: check py2exe"
( cd projects/py2exe; $ARMOR check >result.log 2>&1 )
check_return_value

echo ""
echo "-------------------- Test Command check END --------------------"
echo ""

# ======================================================================
#
#  Command: build
#
# ======================================================================

echo ""
echo "-------------------- Test Command build ------------------------"
echo ""

csih_inform "Case 6.1: build pybench"
( cd projects/pybench; $ARMOR build >result.log 2>&1 )

output=projects/pybench/dist
check_file_exists $output/pybench.py
check_file_content $output/pybench.py 'pyarmor_runtime()'
check_file_content $output/pybench.py '__pyarmor__(__name__'

csih_inform "Case 6.2: build package"
( cd projects/testpkg; $ARMOR build >result.log 2>&1 )

output=projects/testpkg/dist
check_file_exists $output/main.py
check_file_content $output/main.py 'pyarmor_runtime()'
check_file_exists $output/mypkg/__init__.py
check_file_exists $output/mypkg/foo.py
check_file_content $output/mypkg/foo.py '__pyarmor__(__name__'

csih_inform "Case 6.3: build package with entry script in package"
cp examples/testpkg/main.py examples/testpkg/mypkg
( cd projects/testpkg;
    $ARMOR config --entry=main.py >result.log 2>&1 &&
    $ARMOR build -B >result.log 2>&1 )

check_return_value
check_file_exists $output/mypkg/main.py
check_file_content $output/mypkg/main.py 'pyarmor_runtime()'
check_file_content $output/mypkg/main.py '__pyarmor__(__name__'

echo ""
echo "-------------------- Test Command build END --------------------"
echo ""

# ======================================================================
#
#  Command: licenses
#
# ======================================================================

echo ""
echo "-------------------- Test Command licenses ---------------------"
echo ""

csih_inform "Case 7.1: Generate project licenses"
output=projects/pybench/licenses

( cd projects/pybench; $ARMOR licenses code1 code2 code3 \
                       >licenses-result.log 2>&1 )
check_file_exists $output/code1/license.lic
check_file_exists $output/code2/license.lic
check_file_exists $output/code3/license.lic
check_file_exists $output/code1/license.lic.txt

( cd projects/pybench; $ARMOR licenses \
                              --expired $(next_month) \
                              --bind-disk "${harddisk_sn}" \
                              --bind-ipv4 "${ifip_address}" \
                              --bind-mac "${ifmac_address}" \
                              customer-tom >licenses-result.log 2>&1 )
check_file_exists $output/customer-tom/license.lic
check_file_exists $output/customer-tom/license.lic.txt

cat <<EOF > projects/pybench/id_rsa
-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----
EOF
( cd projects/pybench; $ARMOR licenses \
                              --bind-file "id_rsa;id_rsa" \
                              fixkey >licenses-result.log 2>&1 )
check_file_exists $output/fixkey/license.lic
check_file_exists $output/fixkey/license.lic.txt

csih_inform "Case 7.2: Show license info"
( cd projects/pybench; $ARMOR build >licenses-result.log 2>&1 )

cat <<EOF > projects/pybench/dist/info.py
from pytransform import pyarmor_init, get_license_info
pyarmor_init(is_runtime=1)
print(get_license_info())
EOF

( cd projects/pybench/dist;
    $PYTHON info.py >result.log 2>&1 )
check_file_content projects/pybench/dist/result.log "'PyArmor-Project'"

cp $output/code1/license.lic projects/pybench/dist/pytransform
( cd projects/pybench/dist;
    $PYTHON info.py >result.log 2>&1 )
check_file_content projects/pybench/dist/result.log "'code1'"

cp $output/customer-tom/license.lic projects/pybench/dist/pytransform
( cd projects/pybench/dist;
    $PYTHON info.py >result.log 2>&1 )
check_file_content projects/pybench/dist/result.log "'customer-tom'"
check_file_content projects/pybench/dist/result.log "'${harddisk_sn}'"
check_file_content projects/pybench/dist/result.log "'${ifmac_address}'"
check_file_content projects/pybench/dist/result.log "'${ifip_address}'"

cp $output/fixkey/license.lic projects/pybench/dist/pytransform
cp projects/pybench/id_rsa projects/pybench/dist/pytransform
( cd projects/pybench/dist;
    $PYTHON info.py >result.log 2>&1 )
check_file_content projects/pybench/dist/result.log "'\*FIXKEY\*'"

csih_inform "Case 7.3: Generate license which disable all restricts"
output=test-no-restrict-license
$PYARMOR obfuscate -O $output --no-cross-protection \
         examples/simple/queens.py >result.log 2>&1
check_return_value

$PYARMOR licenses --disable-restrict-mode NO-RESTRICT >result.log 2>&1
check_return_value
check_file_exists licenses/NO-RESTRICT/license.lic

cp licenses/NO-RESTRICT/license.lic $output/pytransform/
echo -e "\nprint('No restrict mode')" >> $output/queens.py
(cd $output; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Found 92 solutions'
check_file_content $output/result.log 'No restrict mode'

echo ""
echo "-------------------- Test Command licenses END -----------------"
echo ""

# ======================================================================
#
#  Command: hdinfo
#
# ======================================================================

echo ""
echo "-------------------- Test Command hdinfo -----------------------"
echo ""

csih_inform "Case 8.1: show hardware info"
$PYARMOR hdinfo >result.log 2>&1
check_return_value

csih_inform "Case 8.2: get hardware info"

cat <<EOF > test_get_hd_info.py
import pytransform
from pytransform import pyarmor_init, get_hd_info
pytransform.plat_path = 'platforms'
pyarmor_init(path='.', is_runtime=1)
print(get_hd_info(0))
EOF

$PYTHON test_get_hd_info.py >result.log 2>&1
check_file_content result.log "${harddisk_sn}"

echo ""
echo "-------------------- Test Command hdinfo END -------------------"
echo ""

# ======================================================================
#
#  Command: benchmark
#
# ======================================================================

echo ""
echo "-------------------- Test Command benchmark --------------------"
echo ""

csih_inform "Case 9.1: run benchmark test"
for obf_mod in 0 1 ; do
  for obf_code in 0 1 2 ; do
    for obf_wrap_mode in 0 1 ; do
      csih_inform "obf_mod: $obf_mod, obf_code: $obf_code, wrap_mode: $obf_wrap_mode"
      logfile="log_${obf_mod}_${obf_code}_${obf_wrap_mode}.log"
      $PYARMOR benchmark --obf-mod ${obf_mod} --obf-code ${obf_code} \
                         --wrap-mode ${obf_wrap_mode} >$logfile 2>&1
      check_return_value
      csih_inform "Write benchmark test results to $logfile"
      check_file_content $logfile "run_ten_thousand_obfuscated_bytecode"
      rm -rf .benchtest
    done
  done
done

echo ""
echo "-------------------- Test Command benchmark END ----------------"
echo ""

# ======================================================================
#
#  Use Cases
#
# ======================================================================

echo ""
echo "-------------------- Test Use Cases ----------------------------"
echo ""

csih_inform "Case T-1.1: obfuscate module with project"
$PYARMOR init --src=examples/py2exe --entry=hello.py \
              projects/testmod >result.log 2>&1
$PYARMOR config --manifest="include queens.py" --disable-restrict-mode=1 \
              projects/testmod >result.log 2>&1
(cd projects/testmod; $ARMOR build >result.log 2>&1)

check_file_exists projects/testmod/dist/hello.py
check_file_content projects/testmod/dist/hello.py 'pyarmor_runtime'

check_file_exists projects/testmod/dist/queens.py
check_file_content projects/testmod/dist/queens.py '__pyarmor__(__name__'

(cd projects/testmod/dist; $PYTHON hello.py >result.log 2>&1 )
check_file_content projects/testmod/dist/result.log 'Found 92 solutions'

csih_inform "Case T-1.2: obfuscate module with wraparmor"
PROPATH=projects/testmod_wrap
$PYARMOR init --src=examples/testmod --entry=hello.py $PROPATH >result.log 2>&1
$PYARMOR config --manifest="include queens.py" --disable-restrict-mode=1 \
              --wrap-mode=0 $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_file_exists $PROPATH/dist/hello.py
check_file_content $PROPATH/dist/hello.py 'pyarmor_runtime'

check_file_exists $PROPATH/dist/queens.py
check_file_content $PROPATH/dist/queens.py '__pyarmor__(__name__'

(cd $PROPATH/dist; $PYTHON hello.py >result.log 2>&1 )
check_file_content $PROPATH/dist/result.log 'Found 92 solutions'
check_file_content $PROPATH/dist/result.log '__wraparmor__ can not be called out of decorator'
check_file_content $PROPATH/dist/result.log 'The value of __file__ is OK'
check_file_content $PROPATH/dist/result.log '<frozen queens>'
check_file_content $PROPATH/dist/result.log 'Found frame of function foo'
check_file_content $PROPATH/dist/result.log 'Can not get data from frame.f_locals'
check_file_content $PROPATH/dist/result.log 'Got empty from callback'
check_file_content $PROPATH/dist/result.log 'Generator works well'
check_file_content $PROPATH/dist/result.log 'Shared code object works well'

csih_inform "Case T-1.3: obfuscate module with auto-wrap mode"
PROPATH=projects/testmod_auto_wrap
$PYARMOR init --src=examples/py2exe --entry=queens.py $PROPATH >result.log 2>&1
$PYARMOR config --wrap-mode=1 --disable-restrict-mode=1 \
                --manifest="include queens.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_file_exists $PROPATH/dist/queens.py
check_file_content $PROPATH/dist/queens.py 'pyarmor_runtime'
check_file_content $PROPATH/dist/queens.py '__pyarmor__(__name__'

(cd $PROPATH/dist; $PYTHON queens.py >result.log 2>&1 )
check_file_content $PROPATH/dist/result.log 'Found 92 solutions'

csih_inform "Case T-1.4: obfuscate package with auto-wrap mode"
PROPATH=projects/testpkg_auto_wrap
$PYARMOR init --src=examples/testpkg/mypkg \
              --entry="__init__.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_file_exists $PROPATH/dist/mypkg/__init__.py
check_file_content $PROPATH/dist/mypkg/__init__.py '__pyarmor__(__name__'

cp examples/testpkg/main.py $PROPATH/dist
(cd $PROPATH/dist; $PYTHON main.py >result.log 2>&1 )
check_file_content $PROPATH/dist/result.log 'Hello! PyArmor Test Case'

csih_inform "Case T-1.5: obfuscate 2 independent packages"
output=dist-pkgs
$PYARMOR obfuscate -O $output/pkg1 examples/testpkg/mypkg/__init__.py >result.log 2>&1
$PYARMOR obfuscate -O $output/pkg2 examples/testpkg/mypkg/__init__.py >result.log 2>&1
check_file_exists $output/pkg1/__init__.py
check_file_exists $output/pkg2/__init__.py

cat <<EOF > $output/main.py
from pkg1 import foo as foo1
from pkg2 import foo as foo2

foo1.hello('pkg1')
foo2.hello('pkg2')
EOF

(cd $output; $PYTHON main.py >result.log 2>&1)
check_file_content $output/result.log "Hello! pkg1"
check_file_content $output/result.log "Hello! pkg2"

echo ""
echo "-------------------- Test Use Cases END ------------------------"
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
echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"
