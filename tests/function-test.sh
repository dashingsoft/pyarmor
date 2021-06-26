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
PYARMOR_DATA=~/.pyarmor
if [[ "${PLATFORM}" == "win_amd64" && "${PYTHON}" == *Python38*/python ]] ; then
    [[ -n "$USERPROFILE" ]] && rm -rf "$USERPROFILE\\.pyarmor*" \
        && PYARMOR_DATA=$USERPROFILE\\.pyarmor
fi
csih_inform "PyArmor data at ${PYARMOR_DATA}"

[[ -d data ]] || csih_error "No path 'data' found in current path"
datapath=$(pwd)/data

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

csih_inform "Make path test/data"
mkdir -p test/data
csih_inform "Copy test files from ${datapath} to ./test/data"
cp ${datapath}/*.py test/data
cp -a ${datapath}/sound test/data
cp ${datapath}/project.zip test/data
cp ${datapath}/project.zip test/data/project-orig.zip

if [[ "${PLATFORM}" != "win32" ]] ; then
csih_inform "Make link to platforms for super mode"
if [[ "OK" == $($PYTHON -c'from sys import version_info as ver, stdout
stdout.write("OK" if (ver[0] * 10 + ver[1]) in (27, 37, 38, 39) else "")') ]] ; then
SUPERMODE=yes
mkdir -p ${PYARMOR_DATA}/platforms
PLATFORM_INDEX=${PYARMOR_DATA}/platforms/index.json
if ! [[ -f ${PLATFORM_INDEX} ]] ; then
    csih_inform "Copy platform index.json from pyarmor-core"
    cp ../../../../pyarmor-core/platforms/index.json ${PLATFORM_INDEX}
fi
(cd ${PYARMOR_DATA}/platforms;
 for x in ${PYARMOR_CORE_PLATFORM}/*.py?? ; do
     name=$(basename ${x})
     name=${name//./\/}
     mkdir -p ${name}
     if [[ "${PLATFORM}" == "win_amd64" ]] ; then
         for y in ${x}/pytransform.* ; do
             [[ -f "${y}" ]] && cp ${y} ${name}
         done
     else
         ln -s ${x}/pytransform.* ${name}
     fi
     update_pytransform_hash256 ${PLATFORM_INDEX} ${x}/pytransform.* $(basename ${x})
 done)
fi
csih_inform "Super mode test is ${SUPERMODE}"
fi

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

csih_inform "C-2. Test option --capsule for config"
cp test/data/project.zip projects/test-capsule/project2.zip
$PYARMOR config --capsule=project2.zip projects/test-capsule >result.log 2>&1
check_return_value

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

$PYARMOR licenses --capsule=test/data/project.zip --output=projects/licenses \
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
$PYARMOR obfuscate -O test-no-entry examples/simple >result.log 2>&1
check_return_value
check_file_exists test-no-entry/queens.py

csih_inform "C-8. Test 'gbk' codec for obfuscate"

if [[ "$PYTHON" == C:/Python30/python || "$PYTHON" == *python3.0 ||
          ( "$PLATFORM" == "macosx_x86_64" && "$PYTHON" == *python ) ||
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

csih_inform "C-9. Test --upgrade for capsule (ignored)"
# mkdir -p test-upgrade
# cp test/data/project-orig.zip test-upgrade/.pyarmor_capsule.zip

# $PYARMOR capsule --upgrade ./test-upgrade/ >result.log 2>&1
# check_return_value
# check_file_content result.log "Upgrade capsule OK"

# (cd test-upgrade; unzip .pyarmor_capsule.zip >result.log 2>&1)
# check_file_exists test-upgrade/pytransform.key

csih_inform "C-10. Test output == src for obfuscate"
mkdir -p abc
$PYARMOR obfuscate -O abc abc >result.log 2>&1
check_file_content result.log "Output path can not be same as src"

csih_inform "C-11. Test output is sub-directory of src for obfuscate"
cp -a examples/simple test-subpath
(cd test-subpath;
 $PYTHON ../pyarmor.py obfuscate -O output . >result.log 2>&1)
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
echo "# {PyArmor Plugins}" > test_plugin.py
echo "print('Hello Plugin')" > plugin_hello.py
$PYARMOR obfuscate -O dist-plugin --plugin "plugin_hello" \
         --exact test_plugin.py >result.log 2>&1
check_return_value

(cd dist-plugin; $PYTHON test_plugin.py >result.log 2>&1 )
check_return_value
check_file_content dist-plugin/result.log 'Hello Plugin'

csih_inform "C-19. Test option --plugin with special value 'on'"
mkdir test-plugins
echo "# PyArmor Plugin: print('Hello World')" > test-plugins/foo.py
$PYARMOR obfuscate -O dist-plugin2 --plugin on \
         --exact test-plugins/foo.py >result.log 2>&1
check_return_value

(cd dist-plugin2; $PYTHON foo.py >result.log 2>&1 )
check_return_value
check_file_content dist-plugin2/result.log 'Hello World'

csih_inform "C-20. Test absolute jump critical value in wrap mode"
$PYARMOR obfuscate -O dist-pop-jmp --exact test/data/pop_jmp.py >result.log 2>&1
check_return_value

(cd dist-pop-jmp; $PYTHON pop_jmp.py >result.log 2>&1 )
check_return_value
check_file_content dist-pop-jmp/result.log 'jmp_simple return 3'
check_file_content dist-pop-jmp/result.log 'jmp_short return 30'

csih_inform "C-21. Test last argument is directory for obfuscate"
$PYARMOR obfuscate -O test-path-1 examples/simple  >result.log 2>&1
check_return_value
check_file_exists test-path-1/queens.py

csih_inform "C-22. Test more than one path for obfuscate"
$PYARMOR obfuscate examples/simple examples/testpkg  >result.log 2>&1
check_file_content result.log "Only one path is allowed"

csih_inform "C-23. Test option --bind-data for licenses"
$PYARMOR licenses -x 20191011 test-bind-data >result.log 2>&1
check_return_value
check_file_exists licenses/test-bind-data/license.lic
check_file_content licenses/test-bind-data/license.lic.txt 'test-bind-data;20191011'

csih_inform "C-24. Test option --package-runtime=1 for obfuscate"
$PYARMOR obfuscate --package-runtime 1 --output test-package-runtime \
         examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_exists test-package-runtime/pytransform/__init__.py
check_file_content test-package-runtime/pytransform/__init__.py 'def init_runtime'

(cd test-package-runtime; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content test-package-runtime/result.log 'Found 92 solutions'

(cd test-package-runtime; mkdir another; mv pytransform another;
    PYTHONPATH=another $PYTHON queens.py >result2.log 2>&1 )
check_return_value
check_file_content test-package-runtime/result2.log 'Found 92 solutions'

csih_inform "C-25. Test option --bootstrap=2 for obfuscate"
$PYARMOR obfuscate --package-runtime 1 --bootstrap 2 --output test-bootstrap2 \
         examples/testpkg/mypkg/__init__.py >result.log 2>&1
check_return_value
check_file_exists test-bootstrap2/pytransform/__init__.py
check_file_content test-bootstrap2/pytransform/__init__.py 'def init_runtime'
check_file_exists test-bootstrap2/__init__.py
check_file_content test-bootstrap2/__init__.py 'from pytransform import pyarmor_runtime'

csih_inform "C-25. Test command runtime with default option"
$PYARMOR runtime > result.log 2>&1
check_return_value
check_file_exists dist/pytransform/__init__.py

csih_inform "C-26. Test command obfuscation with --src"
$PYARMOR obfuscate -r --src examples/testpkg -O test-src-path \
         mypkg/foo.py > result.log 2>&1
check_return_value
check_file_exists test-src-path/main.py
check_file_exists test-src-path/mypkg/foo.py
check_file_exists test-src-path/mypkg/__init__.py

csih_inform "C-27. Test no very long line in traceback"
echo "raise Exception('Elinimate long line from traceback')" > e.py
$PYARMOR obfuscate --exact -O test-exception e.py > result.log 2>&1
check_return_value
check_file_exists test-exception/e.py

(cd test-exception; $PYTHON e.py >result.log 2>&1 )
check_file_content test-exception/result.log 'Elinimate long line from traceback'
check_file_content test-exception/result.log '__pyarmor__' not

csih_inform "C-28. Test option --bootstrap=3 for obfuscate"
$PYARMOR obfuscate --package-runtime 1 --bootstrap 3 --output test-bootstrap3 \
         examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_exists test-bootstrap3/pytransform/__init__.py
check_file_content test-bootstrap3/pytransform/__init__.py 'def init_runtime'
check_file_exists test-bootstrap3/queens.py
check_file_content test-bootstrap3/queens.py 'from .pytransform import pyarmor_runtime'

csih_inform "C-29. Test option --exclude .py file for obfuscate"
$PYARMOR obfuscate -O test-exclude3 -r --exclude "mypkg/foo.py" \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-exclude3/main.py
check_file_not_exists test-exclude3/mypkg/foo.py

csih_inform "C-30. Test many entry scripts in exact mode"
echo "" > a.py
echo "" > b.py
echo "" > c.py
output=test-many-scripts
$PYARMOR obfuscate --exact -O $output a.py b.py > result.log 2>&1
check_return_value
check_file_exists $output/a.py
check_file_exists $output/b.py
check_file_not_exists $output/c.py
check_file_content $output/a.py 'import pyarmor_runtime'
check_file_content $output/b.py 'import pyarmor_runtime'

csih_inform "C-31. Output license key to stdout"
$PYARMOR licenses --output stdout reg0001 > result.log 2>&1
check_return_value
check_file_content result.log 'Generate 1 licenses OK.'

csih_inform "C-32. Test multiple option --exclude for obfuscate"
$PYARMOR obfuscate -O test-exclude2 -r --exclude mypkg --exclude dist \
         examples/testpkg/main.py >result.log 2>&1
check_return_value
check_file_exists test-exclude2/main.py
check_file_not_exists test-exclude2/mypkg/foo.py

csih_inform "C-33. Generate license with epoch expired"
$PYARMOR licenses --expired 1579316961.2 reg-epoch-1 > result.log 2>&1
check_return_value
check_file_content result.log 'Generate 1 licenses OK.'
check_file_exists licenses/reg-epoch-1/license.lic

csih_inform "C-34. Test obfuscate script in the non-ascii path"
propath=examples/中文路径
mkdir $propath
cp examples/simple/queens.py $propath
$PYARMOR obfuscate -O test-non-ascii-path $propath/queens.py > result.log 2>&1

check_return_value
check_file_exists test-non-ascii-path/queens.py

(cd test-non-ascii-path; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content test-non-ascii-path/result.log 'Found 92 solutions'

csih_inform "C-35. Test licenses with --fixed"
if [[ "${PYTHON}" == *Python??-32/python ]] ; then
csih_inform "Ignore this case for $PYTHON"
else
propath=test-fixed-key
mkdir $propath
cp examples/simple/queens.py $propath
$PYARMOR licenses --fixed 1 -O $propath/a/license.lic > result.log 2>&1
$PYARMOR licenses --fixed 101 -O $propath/b/license.lic > result.log 2>&1

$PYARMOR obfuscate -O $propath/dist --with-license $propath/a/license.lic \
         $propath/queens.py > result.log 2>&1
(cd $propath/dist; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content $propath/dist/result.log 'Found 92 solutions'

$PYARMOR obfuscate -O $propath/dist --with-license $propath/b/license.lic \
         $propath/queens.py > result.log 2>&1
(cd $propath/dist; $PYTHON queens.py >result.log 2>&1 )
check_file_content $propath/dist/result.log 'License is not for this machine'
check_file_content $propath/dist/result.log 'Found 92 solutions' not
fi

csih_inform "C-36. Test got default capsule from old location"
(cd "${PYARMOR_DATA}"; mv .pyarmor_capsule.zip ..)
$PYARMOR obfuscate -O test-default-capsule examples/simple/queens.py >result.log 2>&1
check_return_value
(cd "${PYARMOR_DATA}" && check_file_exists .pyarmor_capsule.zip)

csih_inform "C-37. Test customized cross protection script"
echo "print('This is customized protection code')" > protection.py
dist=test-c-36
$PYARMOR obfuscate -O $dist --cross-protection protection.py \
         examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log 'This is customized protection code'

csih_inform "C-38. Test obfuscate command with obf-mod is 2"
dist=test-obf-mod-2
$PYARMOR obfuscate -O $dist --obf-mod 2 examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log 'Found 92 solutions'

csih_inform "C-39. Test obfuscate command with inner license"
dist=test-with-license-2
$PYARMOR licenses -e 2020-05-02 r001 >result.log 2>&1
$PYARMOR obfuscate -O $dist --with-license licenses/r001/license.lic \
         examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions' not
check_file_content $dist/result.log 'License is expired'

csih_inform "C-40. Test obfuscate command with special license outer"
dist=test-outer-license
$PYARMOR obfuscate -O $dist --with-license outer examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions' not
check_file_content $dist/result.log 'Read file license.lic failed'

cp licenses/r001/license.lic $dist
(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions' not
check_file_content $dist/result.log 'License is expired'

csih_inform "C-41. Test obfuscate command with --runtime"
dist=test-runtime-1
$PYARMOR runtime -O $dist/runtime >result.log 2>&1
$PYARMOR obfuscate -O $dist/dist --runtime $dist/runtime examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON dist/queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions'

csih_inform "C-42. Test obfuscate command with --runtime and outer license"
dist=test-runtime-2
$PYARMOR runtime -O $dist/runtime --with-license outer >result.log 2>&1
$PYARMOR obfuscate -O $dist/dist --runtime $dist/runtime examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON dist/queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions' not

$PYARMOR licenses -O $dist/dist/pytransform/license.lic >result.log 2>&1
check_file_exists $dist/dist/pytransform/license.lic

(cd $dist; $PYTHON dist/queens.py >result.log 2>&1)
check_file_content $dist/result.log 'Found 92 solutions'

csih_inform "C-43. Test entry script is .pyw"
dist=test-c-43
echo "print('Hello')" > foo.pyw
$PYARMOR obfuscate -O $dist --exact foo.pyw >result.log 2>&1
check_return_value
check_file_exists $dist/foo.pyw
check_file_content $dist/foo.pyw 'from pytransform import pyarmor_runtime'

csih_inform "C-44. Test __del__ works for non-super mode"
if ! [[ "yes" == "${SUPERMODE}" ]] ; then
dist=test-c-44
$PYARMOR obfuscate --exact -O $dist test/data/foo__del.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON foo__del.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "test __del__ OK"
fi

echo ""
echo "-------------------- Command End -----------------------------"
echo ""

# ======================================================================
#
#  Super mode
#
# ======================================================================

if [[ "yes" == "${SUPERMODE}" ]] ; then

echo ""
echo "-------------------- Super Mode ----------------------------"
echo ""

cat <<EOF > sufoo.py
def empty():
  pass
def hello(n):
  empty()
  print('Hello Super Mode: %s' % n)
hello(2)
EOF

csih_inform "S-1. Test basic function of super mode"
dist=dist-super-mode-1
$PYARMOR obfuscate --exact --advanced 2 -O $dist sufoo.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON sufoo.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Hello Super Mode:"

csih_inform "S-2. Test super mode with jump header"
dist=dist-super-mode-2
$PYARMOR obfuscate --exact --advanced 2 -O $dist test/data/no_wrap.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON no_wrap.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Test no wrap obfuscate mode: OK"

csih_inform "S-3. Test super mode with recursive function"
dist=dist-super-mode-3
$PYARMOR obfuscate --exact --advanced 2 -O $dist examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Found 92 solutions"

csih_inform "S-4. Test super mode with obf-code 2"
dist=dist-super-mode-4
$PYARMOR obfuscate --exact --advanced 2 --obf-code 2 -O $dist sufoo.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON sufoo.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Hello Super Mode:"

csih_inform "S-5. Generate runtime files with super mode"
dist=dist-super-mode-5
$PYARMOR runtime -O $dist --super-mode >result.log 2>&1
check_return_value
check_file_exists $dist/pytransform_protection.py

csih_inform "S-6. Test super mode with auto patch"
dist=dist-super-mode-6

cat <<EOF > sufoo2.py
# Test auto patch
import threading
from time import sleep

def foo(n):
  '''This is a test function'''
  while True:
    print('Super Mode: %s' % n)
    break

  k = 0
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  n += 1
  if n > 3:
    print('n is %s' % n)
  sleep(0.5)
  n += 1
  n += 1
  print('At last the value is %s' % n)

for i in range(3):
  threading.Thread(target=foo, args=(i,)).start()
EOF

$PYARMOR obfuscate --exact --advanced 2 -O $dist sufoo2.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON sufoo2.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Super Mode: 2"
check_file_content $dist/result.log "n is 25"
check_file_content $dist/result.log "n is 26"
check_file_content $dist/result.log "n is 27"
check_file_content $dist/result.log "At last the value is 28"

csih_inform "S-7. Test super mode with clean_str"
dist=dist-super-mode-7
cat <<EOF > suclean.py
from sys import version_info as ver
from pytransform import clean_str
data = ('a' * 30) if ver.major == 2 else (b'a' * 30).decode()
print('Clean data: %s' % clean_str(data))
print(data)
EOF

$PYARMOR obfuscate --exact --advanced 2 -O $dist suclean.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON suclean.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Clean data: 30"
check_file_content $dist/result.log "aaaaaaaaaa" not

csih_inform "S-8. Test super mode with obf_mod = 2"
dist=dist-super-mode-8

$PYARMOR obfuscate --exact --advanced 2 -O $dist --obf-mod 2 \
         examples/simple/queens.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Found 92 solutions"

csih_inform "S-9. Test super mode with jump header and obf_code 2"
dist=dist-super-mode-9
$PYARMOR obfuscate --exact --advanced 2 --obf-code 2 -O $dist \
         test/data/no_wrap.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON no_wrap.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Test no wrap obfuscate mode: OK"

csih_inform "S-10. Test special wrap and obf-code is 2"
dist=test-special-wrap-obf-code-2
$PYARMOR obfuscate --exact --advanced 2 --obf-code 2 -O $dist \
         test/data/no_wrap.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON no_wrap.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Test no wrap obfuscate mode: OK"

csih_inform "S-11. Test sub-package with relative import"
dist=test-super-mode-11
mkdir -p $dist/src/pkg/a
echo "" > $dist/src/pkg/__init__.py
echo "" > $dist/src/pkg/a/__init__.py

$PYARMOR obfuscate -r --advanced 2 -O $dist/pkg --bootstrap 3 \
         $dist/src/pkg/__init__.py >result.log 2>&1
check_return_value
check_file_content $dist/pkg/__init__.py "from .pytransform import pyarmor"
check_file_content $dist/pkg/a/__init__.py "from ..pytransform import pyarmor"

$PYARMOR obfuscate -r --advanced 2 -O $dist/dist --bootstrap 3 \
         $dist/src/pkg/__init__.py >result.log 2>&1
check_return_value
check_file_content $dist/dist/__init__.py "from .pytransform import pyarmor"
check_file_content $dist/dist/a/__init__.py "from ..pytransform import pyarmor"

csih_inform "S-12. Test builtin functions locals() and eval()"
dist=test-super-mode-12
cat <<EOF > sulocals.py
def test_locals():
  x = 2
  x = eval('x + 2')
  d = locals()
  print('Local x is %s' % d['x'])
test_locals()
EOF

$PYARMOR obfuscate --exact --advanced 2 -O $dist sulocals.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON sulocals.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Local x is 4"

csih_inform "S-13. Test check_armored in super mode"
dist=test-super-mode-13
cat <<EOF > sfoo13.py
from pytransform import assert_armored

class Queen(object):

    def hello(self):
        print('Hello')

def hello():
    print('Hello')

@assert_armored(Queen.hello)
def hello2():
    print('Hello 2')

EOF
cat <<EOF > smain13.py
def fake_check_armored(*args):
    print('it is fake_check_armored')
    return True
import pytransform
pytransform.check_armored = fake_check_armored

from pytransform import check_armored
import sfoo13 as foo
print('Check armored return: %s' % check_armored(foo.hello, foo.hello2, foo))
EOF

$PYARMOR obfuscate --exact --advanced 2 -O $dist smain13.py sfoo13.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON smain13.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Check armored return: True"
check_file_content $dist/result.log "it is fake_check_armored" not

cp sfoo13.py $dist
(cd $dist; rm -rf sfoo13.pyc __pycache__; $PYTHON smain13.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Check armored return: False"
check_file_content $dist/result.log "it is fake_check_armored" not

csih_inform "S-14. Test check_armored in super mode with restrict mode 4"
dist=test-super-mode-14
$PYARMOR obfuscate --exact --advanced 2 --restrict 4 \
         -O $dist smain13.py sfoo13.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON smain13.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Check armored return: True"
check_file_content $dist/result.log "it is fake_check_armored" not

cp sfoo13.py $dist
(cd $dist; rm -rf sfoo13.pyc __pycache__; $PYTHON smain13.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "Check armored return: False"
check_file_content $dist/result.log "it is fake_check_armored" not

csih_inform "S-15. Test __del__ works in super mode"
dist=test-super-mode-15
$PYARMOR obfuscate --exact --advanced 2 -O $dist \
         test/data/foo__del.py >result.log 2>&1
check_return_value

(cd $dist; $PYTHON foo__del.py >result.log 2>&1)
check_return_value
check_file_content $dist/result.log "test __del__ OK"

echo ""
echo "-------------------- Super Mode End --------------------------"
echo ""

fi

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
 $ARMOR config --output="." --package-runtime=0 >result.log 2>&1;
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

csih_inform "Case P-5: build project with --package-runtime=1"
PROPATH=projects/test-project-package-runtime
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR config --package-runtime=1 $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value

check_file_exists $PROPATH/dist/pytransform/__init__.py
check_file_content $PROPATH/dist/pytransform/__init__.py 'def pyarmor_runtime'

(cd $PROPATH/dist; $PYTHON queens.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'Found 92 solutions'

csih_inform "Case P-6: build project with --bootstrap=2"
PROPATH=projects/test-bootstrap2
$PYARMOR init --src=examples/testpkg/mypkg/ --entry __init__.py $PROPATH  >result.log 2>&1

$PYARMOR config --package-runtime=1 --bootstrap=2 $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value

check_file_exists $PROPATH/dist/mypkg/pytransform/__init__.py
check_file_content $PROPATH/dist/mypkg/pytransform/__init__.py 'def pyarmor_runtime'
check_file_exists $PROPATH/dist/mypkg/__init__.py
check_file_content $PROPATH/dist/mypkg/__init__.py 'from pytransform import pyarmor_runtime'

csih_inform "Case P-7: build project with --restrict-mode=0"
PROPATH=projects/test-p7
$PYARMOR init --src=examples/testpkg/mypkg/ --entry __init__.py $PROPATH  >result.log 2>&1
$PYARMOR config --restrict=0 $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value

check_file_exists $PROPATH/dist/mypkg/pytransform/__init__.py
check_file_exists $PROPATH/dist/mypkg/__init__.py

csih_inform "Case P-8: open project with other configure filename"
PROPATH=projects/test-p8
$PYARMOR init --src=examples/testpkg/mypkg/ --entry __init__.py $PROPATH  >result.log 2>&1
$PYARMOR config --name="Alias-Project-8" $PROPATH  >result.log 2>&1
check_return_value

cp $PROPATH/.pyarmor_config $PROPATH/project.json
(cd $PROPATH; $ARMOR info project.json > result.log 2>&1)
check_return_value
check_file_content $PROPATH/result.log 'Alias-Project-8'

csih_inform "Case P-9: build project with --bootstrap=3"
PROPATH=projects/test-bootstrap3
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR config --package-runtime=1 --bootstrap 3 $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH; $ARMOR build >result.log 2>&1)
check_return_value

check_file_exists $PROPATH/dist/pytransform/__init__.py
check_file_content $PROPATH/dist/pytransform/__init__.py 'def pyarmor_runtime'
check_file_exists $PROPATH/dist/queens.py
check_file_content $PROPATH/dist/queens.py 'from .pytransform import pyarmor_runtime'

csih_inform "Case P-10: Set and clear project plugins and platforms"
PROPATH=projects/test-clear-plugin-platform
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR config --platform linux.x86_64 --plugin check_ntp_time \
         $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR info $PROPATH  >result.log 2>&1
check_file_content result.log "linux.x86_64"
check_file_content result.log "check_ntp_time"

$PYARMOR config --platform "" --plugin "" $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR info $PROPATH  >result.log 2>&1
check_file_content result.log "linux.x86_64" not
check_file_content result.log "check_ntp_time" not

csih_inform "Case P-11: Init project with multiple entries"
PROPATH=projects/test-init-multiple-entry
$PYARMOR init --src=examples --entry simple/queens.py,examples/helloworld/foo.py \
         $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR info $PROPATH  >result.log 2>&1
check_file_content result.log "simple[/\\]queens.py,helloworld[/\\]foo.py"

csih_inform "Case P-12: Config project in other path"
PROPATH=projects/test-config-outer-path
$PYARMOR init --src=examples $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR config --entry "simple/queens.py, examples/helloworld/foo.py" \
         --output $PROPATH/mydist --with-license licpath/license.lic \
         $PROPATH >result.log 2>&1
check_return_value
check_file_content result.log "Format output to mydist"

$PYARMOR info $PROPATH  >result.log 2>&1
check_file_content result.log "simple[/\\]queens.py,helloworld[/\\]foo.py"
check_file_content result.log "mydist"
check_file_content result.log "licpath[/\\]license.lic"

csih_inform "Case P-13: Init project with empty entry"
PROPATH=projects/test-empty-entry-script
$PYARMOR init --src=. --entry="" $PROPATH  >result.log 2>&1
check_return_value
check_file_content $PROPATH/.pyarmor_config '"entry": ""'

csih_inform "Case P-14: Config project with empty entry"
PROPATH=projects/test-config-with-empty-script
$PYARMOR init --src=examples $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR config --entry="" $PROPATH  >result.log 2>&1
check_return_value
check_file_content result.log 'Change project entry to ""'

csih_inform "Case P-15: build project with --with-license"
PROPATH=projects/test-build-with-license
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR build --with-license=outer $PROPATH  >result.log 2>&1
check_return_value
check_file_not_exists exists $PROPATH/dist/pytransform/license.lic

csih_inform "Case P-16: build project with --obf-mod 2"
PROPATH=projects/test-project-with-obf-mod-2
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR config --obf-mod=2 $PROPATH  >result.log 2>&1
check_return_value

$PYARMOR build $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH/dist; $PYTHON queens.py >result.log 2>&1)
check_file_content $PROPATH/dist/result.log 'Found 92 solutions'

csih_inform "Case P-17: build project with --runtime"
PROPATH=projects/test-project-runtime-1
$PYARMOR init --src=examples/simple --entry queens.py $PROPATH  >result.log 2>&1

$PYARMOR runtime -O $PROPATH/runtime >result.log 2>&1
$PYARMOR build --runtime $PROPATH/runtime $PROPATH  >result.log 2>&1
check_return_value

(cd $PROPATH/dist; $PYTHON queens.py >result.log 2>&1)
check_file_content $PROPATH/dist/result.log 'Found 92 solutions'

echo ""
echo "-------------------- Test Project End ------------------------"
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
#  Test settrace/setprofile
#
# ======================================================================

echo ""
echo "-------------------- Test trace/profile --------------------"
echo ""

if [[ "$PYTHON" == C:/Python30/python || "$PYTHON" == *python3.0 ]] ; then
csih_inform "These testcases are ignored in Python30"
else
csih_inform "Case TD-1: run obfuscated functions with sys.settrace"
PROPATH=test-sys-trace-profile
mkdir -p $PROPATH
cat <<EOF > $PROPATH/foo.py
def hello(n):
    n += 1
    return n
print('This is foo.py')
EOF
$PYARMOR obfuscate --exact -O $PROPATH/dist $PROPATH/foo.py >result.log 2>&1
check_return_value

cat <<EOF > $PROPATH/dist/main.py
import sys
import foo

def hello2(n):
    n += 2
    return n

def callback(frame, event, arg):
    print('%s:%s:%s' % (event, frame.f_code.co_name, frame.f_lineno))
    return callback

sys.settrace(callback)
print('foo.hello got %d' % foo.hello(2))
print('hello2 got %d' % hello2(2))
sys.settrace(None)
EOF

(cd $PROPATH/dist; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $PROPATH/dist/result.log 'This is foo.py'
check_file_content $PROPATH/dist/result.log 'call:hello:1'
check_file_content $PROPATH/dist/result.log 'line:hello:2'
check_file_content $PROPATH/dist/result.log 'foo.hello got 3'
check_file_content $PROPATH/dist/result.log 'line:hello:3' not
check_file_content $PROPATH/dist/result.log 'return:hello:3' not
check_file_content $PROPATH/dist/result.log 'call:hello2:4'
check_file_content $PROPATH/dist/result.log 'line:hello2:5'
check_file_content $PROPATH/dist/result.log 'line:hello2:6'
check_file_content $PROPATH/dist/result.log 'return:hello2:6'
check_file_content $PROPATH/dist/result.log 'hello2 got 4'

csih_inform "Case TD-2: run obfuscated functions with threading.settrace"
PROPATH=test-thread-trace-profile
mkdir -p $PROPATH
cat <<EOF > $PROPATH/foo.py
def hello(n):
    n += 1
    return n
print('This is foo.py')
EOF
$PYARMOR obfuscate --exact -O $PROPATH/dist $PROPATH/foo.py >result.log 2>&1
check_return_value

cat <<EOF > $PROPATH/dist/tmain.py
import sys
import foo

def hello2(n):
    n += 2
    return n

def callback(frame, event, arg):
    print('%s:%s:%s' % (event, frame.f_code.co_name, frame.f_lineno))
    return callback

def target():
    print('foo.hello got %d' % foo.hello(2))
    print('hello2 got %d' % hello2(2))
import threading
threading.settrace(callback)
threading.Thread(target=target).start()
EOF
(cd $PROPATH/dist; $PYTHON tmain.py >result.log 2>&1)
check_return_value
check_file_content $PROPATH/dist/result.log 'This is foo.py'
check_file_content $PROPATH/dist/result.log 'call:hello:1'
check_file_content $PROPATH/dist/result.log 'line:hello:2'
check_file_content $PROPATH/dist/result.log 'foo.hello got 3'
check_file_content $PROPATH/dist/result.log 'line:hello:3' not
check_file_content $PROPATH/dist/result.log 'return:hello:3' not
check_file_content $PROPATH/dist/result.log 'call:hello2:4'
check_file_content $PROPATH/dist/result.log 'line:hello2:5'
check_file_content $PROPATH/dist/result.log 'line:hello2:6'
check_file_content $PROPATH/dist/result.log 'return:hello2:6'
check_file_content $PROPATH/dist/result.log 'hello2 got 4'
fi

echo ""
echo "-------------------- Test trace/profile END ------------------"
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

for obf_mod in 0 1 2; do
  for obf_code in 0 1 2 ; do
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

csih_inform "These testcases are ignored in this platform"

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

# Do not work even without obfuscation
if false ; then
csih_inform "Case M-2: run obfuscated scripts with multiprocessing 2"

# sed -i -e "1,2 d" $PROPATH/dist/mp.py

cat <<EOF >> $PROPATH/dist/main.py
from pytransform import pyarmor_runtime
pyarmor_runtime()

import mp
mp.main()
EOF

(cd $PROPATH/dist; $PYTHON main.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'module name: __main__'
check_file_content $PROPATH/dist/result.log 'function f'
check_file_content $PROPATH/dist/result.log 'hello bob'
check_file_content $PROPATH/dist/result.log 'main line'
fi

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
#  Test restrict mode
#
# ======================================================================

echo ""
echo "-------------------- Test restrict mode --------------------"
echo ""

csih_inform "Case RM-0: test restrict mode 0"
output=test-restrict-0
$PYARMOR obfuscate -O $output -r --restrict 0 \
         examples/testpkg/main.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('This is obfuscated foo')" >> $output/mypkg/foo.py
(cd $output; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'
check_file_content $output/result.log 'No restrict mode'

(cd $output; $PYTHON -c 'import main' >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'
check_file_content $output/result.log 'No restrict mode'

(cd $output; echo "import main" > a.py ; $PYTHON a.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'
check_file_content $output/result.log 'No restrict mode'

csih_inform "Case RM-1: test restrict mode 1"
output=test-restrict-1
$PYARMOR obfuscate -O $output -r --restrict 1 \
         examples/testpkg/main.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

(cd $output; $PYTHON -c 'import main' >result.log 2>&1)
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

(cd $output; echo "import main" > a.py ; $PYTHON a.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

cp $output/main.py $output/main.bak
rm -rf $output/main.py? __pycache__
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
(cd $output; $PYTHON main.py >result.log 2>&1)
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'No restrict mode' not
check_file_content $output/result.log 'Check bootstrap restrict mode failed'

cp $output/main.bak $output/main.py
rm -rf $output/mypkg/foo.py? __pycache__ $output/mypkg/__pycache__
echo -e "\nprint('This is obfuscated foo')" >> $output/mypkg/foo.py
(cd $output; $PYTHON main.py >result.log 2>&1)
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'Check restrict mode of module failed'

csih_inform "Case RM-2: test restrict mode 2"
output=test-restrict-2
$PYARMOR obfuscate -O $output -r --restrict 2 \
         examples/testpkg/main.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON main.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

(cd $output; $PYTHON -c 'import main' >result.log 2>&1)
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'Check restrict mode of module failed'

(cd $output; echo "import main" > a.py ; $PYTHON a.py >result.log 2>&1 )
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'Check restrict mode of module failed'

# Do not remove these 3 print statements
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
(cd $output; $PYTHON main.py >result.log 2>&1 )
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'No restrict mode' not
check_file_content $output/result.log 'Check bootstrap restrict mode failed'

csih_inform "Case RM-3: test restrict mode 3"
output=test-restrict-3
$PYARMOR obfuscate -O $output -r --restrict 3 \
         examples/testpkg/main.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON main.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

(cd $output; $PYTHON -c"import main" >result.log 2>&1 )
check_file_content $output/result.log 'Check restrict mode of module failed'

# Do not remove these 3 print statements
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
echo -e "\nprint('No restrict mode')" >> $output/main.py
(cd $output; $PYTHON main.py >result.log 2>&1 )
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'No restrict mode' not
check_file_content $output/result.log 'Check bootstrap restrict mode failed'

csih_inform "Case RM-3.1: test restrict mode 3 with generator function"
output=test-restrict-3.1
cat <<EOF > r3.py
def hello(n):
    print('Hello Generator %s' % n)
def enumerate(sequence, start=0):
    hello(start)
    n = start
    for elem in sequence:
        yield n, elem
        n += 1
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
list(enumerate(seasons, start=1))
EOF
$PYARMOR obfuscate -O $output --exact --restrict 3 r3.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON r3.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello Generator 1'

csih_inform "Case RM-3.2: test restrict mode 3 with lambda function"
output=test-restrict-3.2
cat <<EOF > r3-2.py
def hello():
    print('Hello Lambda')
foo = lambda : hello()
foo()
EOF
$PYARMOR obfuscate -O $output --exact --restrict 3 r3-2.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON r3-2.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello Lambda'

csih_inform "Case RM-3.3: test restrict mode 3 with non-wrap function"
output=test-restrict-3.3
$PYARMOR obfuscate -O $output --exact --restrict 3 \
         test/data/no_wrap.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON no_wrap.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Test no wrap obfuscate mode: OK'

# On Windows for Python2.7~3.3, in multiprocessing/forking.py, function prepare()
#
#    main_module.__name__ = '__main__'
#
# This is problem to set attribute __name__ of restricted main module
#
# On Linux for Python2.7, it will crash even without restrict mode
#
#    Fatal Error: deletion of interned string failed
#
if [[ "OK" == $($PYTHON -c'from sys import version_info as ver, stdout, platform
stdout.write("OK" if (platform == "win32" and (ver[0] * 10 + ver[1]) > 33)
                     or (platform != "win32" and ver[0] == 3) else "")') ]] ; then
csih_inform "Case RM-3.4: test restrict mode 3 with threading and multiprocessing"
output=test-restrict-3.4
$PYARMOR obfuscate -O $output --exact --restrict 3 \
         test/data/tfoo.py test/data/mfoo.py > result.log 2>&1
$PYARMOR obfuscate -O $output --exact --restrict 1 \
         --no-runtime test/data/pub_foo.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON tfoo.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Say hello from function'
check_file_content $output/result.log 'Say hello from module'

(cd $output; $PYTHON mfoo.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'module name: mfoo'
check_file_content $output/result.log 'hello'

if [[ "yes" == "${SUPERMODE}" ]] ; then
csih_inform "Case RM-3.4a: same as 3.4 and enable super mode"
output=test-restrict-3.4a
$PYARMOR obfuscate -O $output --exact --restrict 3 --advanced 2 \
         test/data/tfoo.py test/data/mfoo.py > result.log 2>&1
$PYARMOR obfuscate -O $output --exact --restrict 1 --advanced 2 \
         --no-runtime test/data/pub_foo.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON tfoo.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Say hello from function'
check_file_content $output/result.log 'Say hello from module'

(cd $output; $PYTHON mfoo.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'module name: mfoo'
check_file_content $output/result.log 'hello'
fi
fi

csih_inform "Case RM-4: test restrict mode 4"
output=test-restrict-4
$PYARMOR obfuscate -O $output/mypkg -r --restrict 1 \
         examples/testpkg/mypkg/__init__.py > result.log 2>&1
check_return_value

$PYARMOR obfuscate -O $output/mypkg --exact --restrict 4 \
         --no-bootstrap examples/testpkg/mypkg/foo.py > result.log 2>&1
check_return_value

cp examples/testpkg/main.py $output
(cd $output; $PYTHON main.py >result.log 2>&1 )
check_file_content $output/result.log "ImportError: cannot import name"

(cd $output; $PYTHON -c"import mypkg
mypkg.hello('One')" >result.log 2>&1 )
check_file_content $output/result.log "This function could not be called from the plain script"

(cd $output; $PYTHON -c"import mypkg
mypkg.open_hello('Two')" >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'This is public hello: Two'

(cd $output; $PYTHON -c"import mypkg
mypkg.proxy_hello('Three')" >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'This is proxy hello: Three'
check_file_content $output/result.log 'Hello! Three'

csih_inform "Case RM-4.1: test restrict mode 4 with exception"
output=test-restrict-4.1
mkdir -p $output/mypkg
cat <<EOF > $output/mypkg/__init__.py
from .bar import Testing, print_msg
EOF
cat <<EOF > $output/mypkg/bar.py
class Testing():
    def __init__(self):
        self.key = 'ABCD'
def print_msg():
    print('This is restrict mode 4 testing')
EOF
cat <<EOF > $output/test1.py
from dist import Testing, print_msg
try:
    testing = Testing()
except Exception:
    testing = Testing()
    print('Restrict mode 4 got %s' % testing.key)
EOF
cat <<EOF > $output/test2.py
from dist import Testing, print_msg
try:
    print_msg()
except Exception:
    print_msg()
EOF

$PYARMOR obfuscate -O $output/dist --restrict 1 \
         $output/mypkg/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 4 --bootstrap 0 --exact \
         $output/mypkg/bar.py > result.log 2>&1
check_return_value

(cd $output; $PYTHON test1.py > result.log 2>&1)
check_file_content $output/result.log 'Restrict mode 4 got ABCD' not
check_file_content $output/result.log "This function could not be called from the plain script"

(cd $output; $PYTHON test2.py > result.log 2>&1)
check_file_content $output/result.log 'This is restrict mode 4 testing' not
check_file_content $output/result.log "This function could not be called from the plain script"

csih_inform "Case RM-4.1a: test restrict mode 4 with restirct module attribute"
output=test-restrict-4.1a
$PYARMOR obfuscate -O $output/dist -r --restrict 4 \
         test/data/sound/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 1 --exact \
         test/data/sound/__init__.py > result.log 2>&1
check_return_value

cat <<EOF > $output/foo.py
import dist
from dist import effects, vocoder, formats

print('vocoder password outside is: %s' % vocoder.password)
print('effects.__all__ outside is: %s' % ','.join(effects.__all__))
print('all formsts outside are: %s' % ','.join(formats.namelist))

EOF

(cd $output; $PYTHON foo.py > result.log 2>&1)
check_file_content $output/result.log 'vocoder password outside is: coder-123' not
check_file_content $output/result.log 'effects.__all__ outside: echo,surround' not
check_file_content $output/result.log 'all formsts outside are: wav,mp3' not
check_file_content $output/result.log 'vocoder password inside is: coder-123'
check_file_content $output/result.log 'effects.__all__ inside is: echo,surround'
check_file_content $output/result.log 'all formsts inside are: wav,mp3'

if [[ "yes" == "${SUPERMODE}" ]] ; then
csih_inform "Case RM-4.2: test restrict mode 4 with exception in super mode"
src=test-restrict-4.1
output=test-restrict-4.2
$PYARMOR obfuscate -O $output/dist --restrict 1 --advanced 2 --bootstrap 3 \
         $src/mypkg/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 4 --bootstrap 3 --exact --advanced 2 \
         $src/mypkg/bar.py > result.log 2>&1
check_return_value

cp $src/test*.py $output
(cd $output; $PYTHON test1.py > result.log 2>&1)
check_file_content $output/result.log 'Restrict mode 4 got ABCD' not
check_file_content $output/result.log "This function could not be called from the plain script"

(cd $output; $PYTHON test2.py > result.log 2>&1)
check_file_content $output/result.log 'This is restrict mode 4 testing' not
check_file_content $output/result.log "This function could not be called from the plain script"

csih_inform "Case RM-4.2a: test restirct module attribute in super mode"
output=test-restrict-4.2a
$PYARMOR obfuscate -O $output/dist -r --restrict 4 --advanced 2 \
         --bootstrap 3 test/data/sound/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 1 --exact --advanced 2 \
         --bootstrap 3 test/data/sound/__init__.py > result.log 2>&1
check_return_value

cat <<EOF > $output/foo.py
import dist
from dist import effects, vocoder, formats

print('vocoder password outside is: %s' % vocoder.password)
print('effects.__all__ outside is: %s' % ','.join(effects.__all__))
print('all formsts outside are: %s' % ','.join(formats.namelist))

EOF

(cd $output; $PYTHON foo.py > result.log 2>&1)
check_file_content $output/result.log 'vocoder password outside is: coder-123' not
check_file_content $output/result.log 'effects.__all__ outside: echo,surround' not
check_file_content $output/result.log 'all formsts outside are: wav,mp3' not
check_file_content $output/result.log 'vocoder password inside is: coder-123'
check_file_content $output/result.log 'effects.__all__ inside is: echo,surround'
check_file_content $output/result.log 'all formsts inside are: wav,mp3'
fi

csih_inform "Case RM-5: test restrict mode 5 with exception"
src=test-restrict-4.1
output=test-restrict-5
$PYARMOR obfuscate -O $output/dist --restrict 1 \
         $src/mypkg/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 5 --exact --bootstrap 0 \
         $src/mypkg/bar.py > result.log 2>&1
check_return_value

cp $src/test*.py $output
(cd $output; $PYTHON test1.py > result.log 2>&1)
check_file_content $output/result.log 'Restrict mode 5 got ABCD' not
check_file_content $output/result.log " name '__armor_enter__' is not defined"

(cd $output; $PYTHON test2.py > result.log 2>&1)
check_file_content $output/result.log 'This is restrict mode 4 testing' not
check_file_content $output/result.log " name '__armor_enter__' is not defined"

if [[ "yes" == "${SUPERMODE}" ]] ; then
csih_inform "Case RM-5.1: test restrict mode 5 with exception in super mode"
src=test-restrict-4.1
output=test-restrict-5.1
$PYARMOR obfuscate -O $output/dist --restrict 1 --advanced 2 --bootstrap 3 \
         $src/mypkg/__init__.py > result.log 2>&1
$PYARMOR obfuscate -O $output/dist --restrict 5 --bootstrap 3 --exact --advanced 2 \
         $src/mypkg/bar.py > result.log 2>&1
check_return_value

cp $src/test*.py $output
(cd $output; $PYTHON test1.py > result.log 2>&1)
check_file_content $output/result.log 'Restrict mode 4 got ABCD' not
check_file_content $output/result.log " name '__armor_wrap__' is not defined"

(cd $output; $PYTHON test2.py > result.log 2>&1)
check_file_content $output/result.log 'This is restrict mode 4 testing' not
check_file_content $output/result.log " name '__armor_wrap__' is not defined"
fi

csih_inform "Case RM-bootstrap: test bootstrap mode restrict"
output=test-restrict-bootstrap
$PYARMOR obfuscate -O $output -r --restrict 0 --no-bootstrap \
         examples/testpkg/main.py > result.log 2>&1
check_return_value
check_file_content $output/main.py 'pyarmor_runtime' not

cat <<EOF > $output/a.py
from pytransform import pyarmor_runtime
pyarmor_runtime()
import main
EOF

(cd $output; $PYTHON a.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'Hello! PyArmor Test Case'

rm -rf $output
$PYARMOR obfuscate -O $output -r --restrict 1 --no-bootstrap \
         examples/testpkg/main.py > result.log 2>&1
check_return_value
check_file_content $output/main.py 'pyarmor_runtime' not

cat <<EOF > $output/a.py
from pytransform import pyarmor_runtime
pyarmor_runtime()
import main
EOF

(cd $output; $PYTHON a.py >result.log 2>&1 )
check_file_content $output/result.log 'Hello! PyArmor Test Case' not
check_file_content $output/result.log 'Check bootstrap restrict mode failed'

echo ""
echo "-------------------- Test restrict mode END ----------------"
echo ""

# ======================================================================
#
#  Test plugins
#
# ======================================================================

echo ""
echo "-------------------- Test plugins --------------------"
echo ""

csih_inform "Case Plugin-1: test base features of plugins"
casepath=test-plugins2
mkdir $casepath
cat <<EOF > $casepath/foo.py
# {PyArmor Plugins}
# PyArmor Plugin: msg = "This is print function"
# PyArmor Plugin: print(msg)
# pyarmor_on_p4()

# @pyarmor_test_decorator
def hello():
    pass
hello()

def p5(msg):
    print(msg)
# pyarmor_p5('Plugin 5 should now work')
p5('Call p5 should work')
EOF
cat <<EOF > $casepath/on_p4.py
def on_p4():
    print('This is on demand plugin')
EOF
cat <<EOF > $casepath/test_decorator.py
def test_decorator(f):
    def wrap():
        print('This is decorator plugin')
    return wrap
EOF
echo "print('The unconditional plugin1 works')" > $casepath/p1.py
echo "print('The unconditional plugin2 works')" > $casepath/p2.py
echo "print('The plugin3 should not work')" > $casepath/p3.py

$PYARMOR obfuscate --plugin $casepath/p1 --plugin $casepath/p2 \
         --plugin @$casepath/p3 --plugin @$casepath/on_p4 \
         --plugin @$casepath/test_decorator \
         -O $casepath/dist --exact $casepath/foo.py > result.log 2>&1
check_return_value

(cd $casepath/dist; $PYTHON foo.py > result.log 2>&1)
check_return_value
check_file_content $casepath/dist/result.log 'The unconditional plugin1 works'
check_file_content $casepath/dist/result.log 'The unconditional plugin2 works'
check_file_content $casepath/dist/result.log 'The plugin3 should not work' not
check_file_content $casepath/dist/result.log 'This is print function'
check_file_content $casepath/dist/result.log 'This is on demand plugin'
check_file_content $casepath/dist/result.log 'This is decorator plugin'
check_file_content $casepath/dist/result.log 'Call p5 should work'
check_file_content $casepath/dist/result.log 'Plugin 5 should now work' not

csih_inform "Case Plugin-2: test plugin in the default path"
echo "# {PyArmor Plugins}" > $casepath/foo2.py
echo "# {PyArmor Plugin} check_ntp_time()" >> $casepath/foo2.py

PYTHONDEBUG=y $PYARMOR obfuscate --plugin check_ntp_time \
              -O $casepath/dist2 --exact $casepath/foo2.py > result.log 2>&1
check_return_value

check_file_exists $casepath/foo2.py.pyarmor-patched
check_file_content $casepath/foo2.py.pyarmor-patched 'class NTPClient'

csih_inform "Case Plugin-3: test internal plugin: assert_armored"
casepath=test_plugin_assert_armored
mkdir -p $casepath
cat <<EOF > $casepath/foo.py
def connect(username, password):
    print('password is %s' % password)
EOF
cat <<EOF > $casepath/main.py
import foo

# PyArmor Plugin: from pytransform import assert_armored
# PyArmor Plugin: @assert_armored(foo.connect)
def start_server():
    foo.connect('root', 'admin')
start_server()
EOF

$PYARMOR obfuscate --plugin on -O $casepath/dist \
         $casepath/main.py  > result.log 2>&1
check_return_value

(cd $casepath/dist; $PYTHON main.py > result.log 2>&1)
check_return_value
check_file_content $casepath/dist/result.log "password is admin"

rm -rf $casepath/dist/foo.* $casepath/dist/__pycache__
cp $casepath/{foo.py,dist}
(cd $casepath; $PYTHON dist/main.py > result.log 2>&1)
check_file_content $casepath/result.log "password is admin" not
check_file_content $casepath/result.log "Protection Fault: this function is not pyarmored"

if [[ "yes" == "${SUPERMODE}" ]] ; then
csih_inform "Case Plugin-4: test internal plugin: assert_armored in super mode"
casepath=test_plugin_assert_armored_2
mkdir -p $casepath
cat <<EOF > $casepath/foo.py
def connect(username, password):
    print('password is %s' % password)
EOF
cat <<EOF > $casepath/main.py
import foo

# PyArmor Plugin: from pytransform import assert_armored
# PyArmor Plugin: @assert_armored(foo.connect)
def start_server():
    foo.connect('root', 'admin')
start_server()
EOF

$PYARMOR obfuscate --advanced 2 --plugin on -O $casepath/dist \
         $casepath/main.py  > result.log 2>&1
check_return_value

(cd $casepath/dist; $PYTHON main.py > result.log 2>&1)
check_return_value
check_file_content $casepath/dist/result.log "password is admin"

rm -rf $casepath/dist/foo.* $casepath/dist/__pycache__
cp $casepath/{foo.py,dist}
(cd $casepath; $PYTHON dist/main.py > result.log 2>&1)
check_file_content $casepath/result.log "password is admin" not
check_file_content $casepath/result.log "Protection fault"
fi

echo ""
echo "-------------------- Test plugins END ----------------"
echo ""

# ======================================================================
#
#  Test bootstrap package
#
# ======================================================================

echo ""
echo "-------------------- Test bootstrap package --------------------"
echo ""

csih_inform "Case BP-01: generate runtime package and bootstrap script"
output=test-bootstrap-1
$PYARMOR runtime -O $output > result.log 2>&1
check_return_value
check_file_exists  $output/pytransform/__init__.py
check_file_exists  $output/pytransform_bootstrap.py
check_file_content $output/pytransform_bootstrap.py 'from pytransform import pyarmor_runtime'

echo "import pytransform_bootstrap" > $output/main.py
echo "print('OK')" >> $output/main.py
(cd $output; $PYTHON main.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'OK'

csih_inform "Case BP-02: generate runtime package and bootstrap package"
output=test-bootstrap-2
$PYARMOR runtime -O $output -i > result.log 2>&1
check_return_value
check_file_exists  $output/pytransform_bootstrap/pytransform/__init__.py
check_file_exists  $output/pytransform_bootstrap/__init__.py
check_file_content $output/pytransform_bootstrap/__init__.py 'from .pytransform import pyarmor_runtime'

echo "import pytransform_bootstrap" > $output/main.py
echo "print('OK2')" >> $output/main.py
(cd $output; $PYTHON main.py >result.log 2>&1 )
check_return_value
check_file_content $output/result.log 'OK2'

csih_inform "Case BP-03: generate runtime files with --no-package"
output=test-runtime-no-package
$PYARMOR runtime --no-package -O $output > result.log 2>&1
check_return_value
check_file_exists  $output/pytransform.py

csih_inform "Case BP-04: generate runtime files with --enable-suffix"
output=test-enable-suffix-no-package
$PYARMOR runtime --no-package --enable-suffix -O $output > result.log 2>&1
check_return_value
check_file_exists  $output/pytransform.py

output=test-enable-suffix-package
$PYARMOR runtime --enable-suffix -O $output > result.log 2>&1
check_return_value
check_file_exists  $output/pytransform/__init__.py

echo ""
echo "-------------------- Test bootstrap package END ----------------"
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
