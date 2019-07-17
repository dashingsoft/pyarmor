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
cp ${datapath}/project.zip test/data/project-orig.zip

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
$PYARMOR obfuscate --capsule=test-capsule/.pyarmor-capsule.zip \
         --output=dist-capsule examples/simple/queens.py \
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
$PYARMOR obfuscate --recursive -O dist-recursive \
         examples/simple/queens.py >result.log 2>&1
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
cp test/data/gbk.py test-codec
$PYARMOR obfuscate -O dist-codec test-codec/gbk.py >result.log 2>&1
check_return_value
check_file_exists dist-codec/gbk.py

(cd dist-codec; $PYTHON gbk.py >result.log 2>&1 )
check_return_value
check_file_content dist-codec/result.log 'PyArmor'
fi

csih_inform "C-9. Test --upgrade for capsule"
mkdir -p test-upgrade
cp test/data/project-orig.zip test-upgrade/.pyarmor_capsule.zip

$PYARMOR capsule --upgrade ./test-upgrade/ >result.log 2>&1
check_return_value
check_file_content result.log "Upgrade capsule OK"

(cd test-upgrade; unzip .pyarmor_capsule.zip >result.log 2>&1)
check_file_exists test-upgrade/pytransform.key

csih_inform "C-10. Test output == src for obfuscate"
$PYARMOR obfuscate --src=abc -O abc >result.log 2>&1
check_file_content result.log "Output path can not be same as src"

csih_inform "C-11. Test output is sub-directory of src for obfuscate"
cp -a examples/simple test-subpath
(cd test-subpath;
 $PYTHON ../pyarmor.py obfuscate --src=. -O output >result.log 2>&1)
check_return_value
check_file_exists test-subpath/output/queens.py

csih_inform "C-12. Test utf-8 with BOM for obfuscate"
mkdir -p test-utf8bom
cp test/data/utf8bom.py test-utf8bom
$PYARMOR obfuscate -O dist-utf8bom test-utf8bom/utf8bom.py >result.log 2>&1
check_return_value
check_file_exists dist-utf8bom/utf8bom.py

(cd dist-utf8bom; $PYTHON utf8bom.py >result.log 2>&1 )
check_return_value
check_file_content dist-utf8bom/result.log 'PyArmor'

csih_inform "C-13. Test option --exclude for obfuscate"
$PYARMOR obfuscate -O test-exclude -r --exclude "mypkg,dist" \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-exclude/main.py
check_file_not_exists test-exclude/mypkg/foo.py

csih_inform "C-13-a. Test multiple option --exclude for obfuscate"
$PYARMOR obfuscate -O test-exclude2 -r --exclude mypkg --exclude dist \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-exclude2/main.py
check_file_not_exists test-exclude2/mypkg/foo.py

csih_inform "C-14. Test option --exact for obfuscate"
$PYARMOR obfuscate -O test-exact --exact \
         examples/testpkg/mypkg/foo.py >result.log 2>&1
check_return_value
check_file_exists test-exact/foo.py
check_file_not_exists test-exact/__init__.py

csih_inform "C-15. Test package for obfuscate"
$PYARMOR obfuscate -O test-package/mypkg \
         examples/testpkg/mypkg/__init__.py >result.log 2>&1
check_return_value
check_file_exists test-package/mypkg/foo.py
check_file_exists test-package/mypkg/__init__.py

(cd test-package; $PYTHON -c "import mypkg" >result.log 2>&1 )
check_return_value

csih_inform "C-16. Test option --no-bootstrap for obfuscate"
$PYARMOR obfuscate -O test-no-bootstrap --no-bootstrap \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-no-bootstrap/main.py
check_file_content test-no-bootstrap/main.py "pyarmor_runtime" not

csih_inform "C-17. Test option --no-cross-protection for obfuscate"
$PYARMOR obfuscate -O test-no-cross-protection --no-cross-protection \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-no-cross-protection/main.py

csih_inform "C-18. Test option --plugin for obfuscate"
echo "print('Hello Plugin')" > plugin_hello.py
$PYARMOR obfuscate -O dist-plugin --plugin "plugin_hello" \
         examples/simple/queens.py >result.log 2>&1
check_return_value

(cd dist-plugin; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content dist-plugin/result.log 'Hello Plugin'
check_file_content dist-plugin/result.log 'Found 92 solutions'

csih_inform "C-19. Test option --plugin with PYARMOR_PLUGIN for obfuscate"
mkdir test-plugins
echo "print('Hello World')" > test-plugins/hello2.py
PYARMOR_PLUGIN=test-plugins $PYARMOR obfuscate -O dist-plugin2 \
              --plugin hello2 examples/simple/queens.py >result.log 2>&1
check_return_value

(cd dist-plugin2; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content dist-plugin2/result.log 'Hello World'
check_file_content dist-plugin2/result.log 'Found 92 solutions'

csih_inform "C-20. Test absolute jump critical value in wrap mode"
$PYARMOR obfuscate -O dist-pop-jmp --exact test/data/pop_jmp.py >result.log 2>&1
check_return_value

(cd dist-pop-jmp; $PYTHON pop_jmp.py >result.log 2>&1 )
check_return_value
check_file_content dist-pop-jmp/result.log 'jmp_simple return 3'
check_file_content dist-pop-jmp/result.log 'jmp_short return 30'

echo ""
echo "-------------------- Command End -----------------------------"
echo ""

# ======================================================================
#
#  Project
#
# ======================================================================

echo ""
echo "-------------------- Test Project ----------------------------"
echo ""

csih_inform "Case P-1: project output path is '.'"
PROPATH=projects/test-blank-ouput
$PYARMOR init --src=examples/simple $PROPATH >result.log 2>&1
check_return_value

(cd $PROPATH;
 $ARMOR config --output="." >result.log 2>&1;
 $ARMOR build >result.log 2>&1)
check_return_value
check_file_exists $PROPATH/queens.py
check_file_exists $PROPATH/pytransform.py

csih_inform "Case P-2: project output path is sub-directory of src"
PROPATH=projects/test-project-output
cp -a examples/simple $PROPATH
$PYARMOR init --src=$PROPATH $PROPATH  >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value
check_file_exists $PROPATH/dist/queens.py

(cd $PROPATH; $ARMOR build -B >result.log 2>&1)
check_return_value
check_file_exists $PROPATH/dist/queens.py
check_file_not_exists $PROPATH/dist/dist/queens.py

csih_inform "Case P-3: project entry script is not in the src path"
PROPATH=projects/test-entry
mkdir -p $PROPATH/scripts
cat <<EOF > $PROPATH/scripts/foo.py
#! /usr/bin/env python
print('Hello')
EOF
$PYARMOR init --src=$PROPATH --entry scripts/foo.py $PROPATH  >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value
check_file_exists $PROPATH/dist/scripts/foo.py
check_file_content $PROPATH/dist/scripts/foo.py '#! /usr/bin/env python'
check_file_content $PROPATH/dist/scripts/foo.py 'pyarmor_runtime'
check_file_content $PROPATH/dist/scripts/foo.py 'print' not

csih_inform "Case P-4: no leading dot is inserted into entry script without runtime"
PROPATH=projects/test-package-init
$PYARMOR init --src=examples/testpkg/mypkg/ --entry __init__.py $PROPATH  >result.log 2>&1
(cd $PROPATH; $ARMOR build --no-runtime >result.log 2>&1)
check_return_value

check_file_exists $PROPATH/dist/mypkg/__init__.py
check_file_content $PROPATH/dist/mypkg/__init__.py 'from pytransform import pyarmor_runtime'
check_file_content $PROPATH/dist/mypkg/__init__.py 'pyarmor_runtime'

echo ""
echo "-------------------- Test Project End ------------------------"
echo ""

# ======================================================================
#
#  Project Child
#
# ======================================================================

echo ""
echo "-------------------- Test Project Child -----------------------"
echo ""

csih_inform "Case PC-1: create child project 1"
PROPATH=projects/test-child-project
$PYARMOR init --src=examples/simple $PROPATH >result.log 2>&1
$PYARMOR init --child 1 $PROPATH >result.log 2>&1

check_return_value
check_file_exists $PROPATH/.pyarmor_config.1

csih_inform "Case PC-2: config child project 1"
(cd $PROPATH;
 $ARMOR config --plugin="hello" --plugin="hello2" \
        --manifest "include queens.py" 1 >result.log 2>&1)

check_return_value

csih_inform "Case PC-3: show information of child project 1"
(cd $PROPATH;  $ARMOR info 1 >result.log 2>&1)

check_return_value
check_file_content $PROPATH/result.log "manifest: include queens.py"
check_file_content $PROPATH/result.log "hello2"

csih_inform "Case PC-4: build child project 1"
(cd $PROPATH; $ARMOR build --no-runtime 1 >result.log 2>&1)

check_return_value
check_file_exists $PROPATH/dist/queens.py
check_file_not_exists $PROPATH/dist/pytransform.py

csih_inform "Case PC-5: clear plugin for child project 1"
(cd $PROPATH;
 $ARMOR config --plugin clear 1 >result.log 2>&1)
check_return_value

(cd $PROPATH;  $ARMOR info 1 >result.log 2>&1)
check_return_value
check_file_content $PROPATH/result.log "hello2" not

echo ""
echo "-------------------- Test Project Child End -------------------"
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
$PYARMOR obfuscate --platform linux64 -O test-cross-publish \
         examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_content result.log "Target dynamic library"
check_file_content result.log "linux64[/\\]_pytransform.so"

csih_inform "Case CP-2: cross publish by obfuscate with no-cross-protection"
$PYARMOR obfuscate --platform linux64 -O test-cross-publish \
         --no-cross-protection examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_content result.log "Target dynamic library" not
check_file_content result.log "linux64[/\\]_pytransform.so"

csih_inform "Case CP-3: cross publish by project"
PROPATH=projects/test-cross-publish
$PYARMOR init --src examples/simple --entry queens.py $PROPATH >result.log 2>&1
$PYARMOR build --platform linux64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "Target dynamic library"
check_file_content result.log "linux64[/\\]_pytransform.so"

csih_inform "Case CP-4: cross publish by project without cross-protection"
$PYARMOR config --cross-protection 0 $PROPATH >result.log 2>&1
check_return_value

$PYARMOR build -B --platform linux64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "Target dynamic library" not
check_file_content result.log "linux64[/\\]_pytransform.so"

csih_inform "Case CP-5: cross publish by project with custom cross protection"
$SED -i -e 's/"cross_protection": [01]/"cross_protection": "protect_code.pt"/g' \
    $PROPATH/.pyarmor_config >result.log 2>&1
check_return_value
check_file_content $PROPATH/.pyarmor_config "protect_code.pt"

$PYARMOR build -B --platform linux64 $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "Target dynamic library"
check_file_content result.log "linux64[/\\]_pytransform.so"

echo ""
echo "-------------------- Test Cross Publish END ------------------------"
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
#  Test empty script
#
# ======================================================================

echo ""
echo "-------------------- Test empty script --------------------"
echo ""

mkdir test-empty
echo "" > test-empty/foo.py
$PYARMOR init --src=test-empty --entry=foo.py projects/empty  > result.log 2>&1
check_return_value

for obf_mod in 0 1 ; do
  for obf_code in 0 1 ; do
    for obf_wrap_mode in 0 1 ; do
      csih_inform "T-m${obf_mod}-c${obf_code}-w${obf_wrap_mode}"
      (cd projects/empty &&
          $ARMOR config --obf-mod ${obf_mod} --obf-code ${obf_code} \
                        --wrap-mode ${obf_wrap_mode} > result.log 2>&1)
      check_return_value

      (cd projects/empty && $ARMOR build -B > result.log 2>&1)
      check_return_value
      check_file_exists "projects/empty/dist/foo.py"

      (cd projects/empty/dist; $PYTHON foo.py > result.log 2>&1)
      check_return_value
    done
  done
done

echo ""
echo "-------------------- Test empty script END ----------------"
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
#  Test non-ascii path
#
# ======================================================================

echo ""
echo "-------------------- Test non-ascii path --------------------"
echo ""

csih_inform "Case I18N-1: run obfuscated scripts in zh-CN path"
output=中文路径
$PYARMOR obfuscate -O $output/dist examples/simple/queens.py  > result.log 2>&1
check_return_value

(cd $output; $PYTHON dist/queens.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Found 92 solutions'

echo ""
echo "-------------------- Test non-ascii path END ----------------"
echo ""

# ======================================================================
#
#  Test lambda function
#
# ======================================================================

echo ""
echo "-------------------- Test lambda function --------------------"
echo ""

csih_inform "Case LF-1: lambda function should not be obfuscated"

cat <<EOF >> test-lambda.py
f = lambda x: x**2
print('pow(8, 2) = %d' % f(8))
co = f.func_code if hasattr(f, 'func_code') else f.__code__
print('len(co_names) is %s' % len(co.co_names))
EOF

output=test-lambda
$PYARMOR obfuscate -O $output --exact test-lambda.py  > result.log 2>&1
check_return_value

(cd $output; $PYTHON test-lambda.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'pow(8, 2) = 64'
check_file_content $output/result.log 'len(co_names) is 0'

csih_inform "Case LF-2: no obfuscate function like 'lambda_*'"

cat <<EOF >> test-lambda2.py
def lambda_f(x):
    return x**2
print('pow(8, 2) = %d' % lambda_f(8))
co = lambda_f.func_code if hasattr(lambda_f, 'func_code') else lambda_f.__code__
print('len(co_names) is %s' % len(co.co_names))
EOF

output=test-lambda2
$PYARMOR obfuscate -O $output --exact test-lambda2.py  > result.log 2>&1
check_return_value

(cd $output; $PYTHON test-lambda2.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'pow(8, 2) = 64'
check_file_content $output/result.log 'len(co_names) is 0'

echo ""
echo "-------------------- Test lambda function END ----------------"
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
