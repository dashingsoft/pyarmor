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

datafile=$(pwd)/data/pyarmor-data.tar.gz

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && mv src/* ./

csih_inform "Extract test data"
mkdir data && (cd data; tar xzf $datafile)

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
# Start test with trial version.
#
# ======================================================================

echo ""
echo "-------------------- Test Trial Version ------------------------"
echo ""

csih_inform "1. Show version information"
$PYARMOR --version >result.log 2>&1 || csih_bug "show version FAILED"

csih_inform "2. Obfuscate foo.py"
$PYARMOR obfuscate examples/helloworld/foo.py >result.log 2>&1
check_return_value

csih_inform "3. Run obfuscated foo.py"
(cd dist; $PYTHON foo.py >result.log 2>&1)
check_return_value
check_file_content dist/result.log "is never expired"
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

csih_inform "4. Import obfuscated package"
$PYARMOR obfuscate -O dist/mypkg examples/testpkg/mypkg/__init__.py >result.log 2>&1
(cd dist; $PYTHON -c "from mypkg import foo
foo.hello('pyarmor')"  >result.log 2>&1)
check_return_value
check_file_content dist/result.log "Hello!"

csih_inform "5. Run big array scripts"
ascript="big_array.py"
$PYTHON -c"
with open('$ascript', 'w') as f:
  for i in range(100):
    f.write('a{0} = {1}\n'.format(i, [1] * 1000))"
$PYARMOR obfuscate --exact -O dist-big-array $ascript >result.log 2>&1
check_file_content result.log 'Obfuscate co failed'
check_file_content result.log 'Too big code object, the limitation is'

csih_inform "6: obfuscate big code object without wrap mode"
PROPATH=projects/test_big_code_object
$PYTHON -c"
with open('big_array.py', 'w') as f:
  for i in range(100):
    f.write('a{0} = {1}\n'.format(i, [1] * 1000))
  f.write('print(\"a99 = %s\" % a99)')"
$PYARMOR init --src=. --entry=big_array.py -t app $PROPATH >result.log 2>&1
$PYARMOR config --wrap-mode=0 --manifest="include big_array.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_file_content $PROPATH/result.log 'Obfuscate co failed'
check_file_content $PROPATH/result.log 'Too big code object, the limitation is'

csih_inform "7. Import many obfuscated packages"
PROPATH=test-many-packages
mkdir -p $PROPATH/pkg1
mkdir -p $PROPATH/pkg2
echo "name = 'This is first package'" > $PROPATH/pkg1/__init__.py
echo "name = 'This is second package'" > $PROPATH/pkg2/__init__.py

$PYARMOR init --src=$PROPATH/pkg1 --entry=__init__.py $PROPATH/pkg1 >result.log 2>&1
$PYARMOR init --src=$PROPATH/pkg2 --entry=__init__.py $PROPATH/pkg2 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --no-runtime $PROPATH/pkg1 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --no-runtime $PROPATH/pkg2 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --only-runtime $PROPATH/pkg1 >result.log 2>&1

cat <<EOF > $PROPATH/obf/main.py
from pkg1 import name as pkg_name1
from pkg2 import name as pkg_name2
print(pkg_name1)
print(pkg_name2)
EOF
(cd $PROPATH/obf; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $PROPATH/obf/result.log 'This is first package'
check_file_content $PROPATH/obf/result.log 'This is second package'

csih_inform "8. Obfuscate scripts with advanced mode"
$PYARMOR obfuscate --advanced --output dist-trial-advanced \
         examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_exists dist-trial-advanced/queens.py

(cd dist-trial-advanced; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content dist-trial-advanced/result.log 'Found 92 solutions'

csih_inform "9. Obfuscate scripts with advanced mode but more than 30 functions"
let -i n=0
while (( n < 36 )) ; do
    (( n++ ))
    echo "def foo$n(i):
    return i + 1" >> t32.py
done
echo "print('Hello world')" >> t32.py

$PYARMOR obfuscate --advanced --output dist-trial-advanced-2 --exact t32.py >result.log 2>&1
check_file_content result.log 'In trial version the limitation is about'

# ======================================================================
#
# Start test with normal version.
#
# ======================================================================

echo ""
echo "-------------------- Test Normal Version ------------------------"
echo ""

csih_inform "Replacing trial license.lic with normal one"
cp data/license.lic .
touch license.lic

csih_inform "1. Show version information"
$PYARMOR --version >result.log 2>&1

csih_inform "2. Obfuscate foo.py"
$PYARMOR obfuscate examples/helloworld/foo.py >result.log 2>&1
check_return_value

csih_inform "3. Run obfuscated foo.py"
(cd dist; $PYTHON foo.py >result.log 2>&1)
check_return_value
check_file_content dist/result.log "is never expired"
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

csih_inform "4. Import obfuscated package"
$PYARMOR obfuscate -O dist/mypkg examples/testpkg/mypkg/__init__.py >result.log 2>&1
(cd dist; $PYTHON -c "from mypkg import foo
foo.hello('pyarmor')"  >result.log 2>&1)
check_return_value
check_file_content dist/result.log "Hello!"

csih_inform "5. Run big array scripts"
ascript="big_array.py"
$PYTHON -c"
with open('$ascript', 'w') as f:
  for i in range(100):
    f.write('a{0} = {1}\n'.format(i, [1] * 1000))"
$PYARMOR obfuscate --exact -O dist-big-array $ascript >result.log 2>&1
check_return_value

csih_inform "6: obfuscate big code object without wrap mode"
PROPATH=projects/test_big_code_object
$PYTHON -c"
with open('big_array.py', 'w') as f:
  for i in range(100):
    f.write('a{0} = {1}\n'.format(i, [1] * 1000))
  f.write('print(\"a99 = %s\" % a99)')"
$PYARMOR init --src=. --entry=big_array.py -t app $PROPATH >result.log 2>&1
$PYARMOR config --wrap-mode=0 --manifest="include big_array.py" $PROPATH >result.log 2>&1
(cd $PROPATH; $ARMOR build >result.log 2>&1)

check_file_exists $PROPATH/dist/big_array.py
check_file_content $PROPATH/dist/big_array.py 'pyarmor_runtime'
check_file_content $PROPATH/dist/big_array.py '__pyarmor__(__name__'

(cd $PROPATH/dist; $PYTHON big_array.py >result.log 2>&1 )
check_return_value
check_file_content $PROPATH/dist/result.log 'a99 ='

csih_inform "7. Import many obfuscated packages"
PROPATH=test-many-packages
mkdir -p $PROPATH/pkg1
mkdir -p $PROPATH/pkg2
echo "name = 'This is first package'" > $PROPATH/pkg1/__init__.py
echo "name = 'This is second package'" > $PROPATH/pkg2/__init__.py

$PYARMOR init --src=$PROPATH/pkg1 --entry=__init__.py $PROPATH/pkg1 >result.log 2>&1
$PYARMOR init --src=$PROPATH/pkg2 --entry=__init__.py $PROPATH/pkg2 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --no-runtime $PROPATH/pkg1 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --no-runtime $PROPATH/pkg2 >result.log 2>&1
$PYARMOR build --output $PROPATH/obf --only-runtime $PROPATH/pkg1 >result.log 2>&1

cat <<EOF > $PROPATH/obf/main.py
from pkg1 import name as pkg_name1
from pkg2 import name as pkg_name2
print(pkg_name1)
print(pkg_name2)
EOF
(cd $PROPATH/obf; $PYTHON main.py >result.log 2>&1)
check_return_value
check_file_content $PROPATH/obf/result.log 'This is first package'
check_file_content $PROPATH/obf/result.log 'This is second package'

csih_inform "8. Obfuscate scripts with advanced mode"
$PYARMOR obfuscate --advanced --output dist-advanced examples/simple/queens.py >result.log 2>&1
check_return_value
check_file_exists dist-advanced/queens.py

(cd dist-advanced; $PYTHON queens.py >result.log 2>&1)
check_return_value
check_file_content dist-advanced/result.log 'Found 92 solutions'

csih_inform "9. Obfuscate scripts with advanced mode but more than 30 functions"
$PYARMOR obfuscate --advanced --output dist-advanced-2 --exact t32.py >result.log 2>&1
check_return_value
check_file_exists dist-advanced-2/t32.py

(cd dist-advanced-2; $PYTHON t32.py >result.log 2>&1)
check_return_value
check_file_content dist-advanced-2/result.log 'Hello world'

# ======================================================================
#
# Finished and cleanup.
#
# ======================================================================

csih_inform "Remove global capsule"
rm -rf ~/.pyarmor_capsule.zip*

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
