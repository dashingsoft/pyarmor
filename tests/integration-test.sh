#! /bin/bash

UNAME=$(uname)
if [[ ${UNAME:0:5} == Linux ]] ; then
    if [[ $(arch) == x86_64 ]] ; then
        PLATFORM=linux_x86_64
    else
        PLATFORM=linux_i386
    fi
    PKGEXT=tar.bz2
else

    if [[ $(uname) == Darwin ]] ; then
        PLATFORM=macosx_x86_64
        PKGEXT=tar.bz2
    else
        if [[ $(arch) == x86_64 ]] ; then
            PLATFORM=win_amd64
        else
            PLATFORM=win32
        fi
        PKGEXT=zip
    fi
fi

# From pyarmor 3.5.1, dist is moved to top level
DIST="../dist"
[[ -d "../dist" ]] || DIST="../src/dist"
filename=$(cd ${DIST}; ls -t pyarmor-*.${PKGEXT}) || exit 1
version=${filename:8:6}
if [[ "${version:5:1}" == "." ]] ; then
    version=${filename:8:5}
fi
extchar=${PYARMOR_EXTRA_CHAR:-e}
workpath=__runtest__
datafile=$(pwd)/data/pyarmor-data.tar.gz
pkgfile=$(pwd)/${DIST}/pyarmor-${version}.${PKGEXT}

declare -i _bug_counter=0

case ${PLATFORM} in

    win32)
        PYTHON=${PYTHON:-C:/Python26/python}
        declare -r harddisk_sn=013040BP2N80S13FJNT5
        declare -r ifmac_address=70:f1:a1:23:f0:94
        declare -r ifip_address=192.168.121.101
        declare -r domain_name=
        ;;
    win_amd64)
        PYTHON=${PYTHON:-C:/Python26/python}
        declare -r harddisk_sn=VBa2fd0ee8-4482c1ad
        declare -r ifmac_address=08:00:27:51:d9:fe
        declare -r ifip_address=192.168.121.112
        # Dell Win7
        # declare -r ifip_address=169.254.225.168
        declare -r domain_name=
        ;;
    linux_i386)
        PYTHON=${PYTHON:-python}
        declare -r harddisk_sn=VB07ab3ff6-81eb5787
        declare -r ifmac_address=08:00:27:88:4b:88
        declare -r ifip_address=192.168.121.106
        declare -r domain_name=
        ;;
    linux_x86_64)
        PYTHON=${PYTHON:-python}
        declare -r harddisk_sn=9WK3FEMQ
        declare -r ifmac_address=00:23:8b:e0:4f:a7
        declare -r ifip_address=192.168.121.103
        declare -r domain_name=
        ;;
    macosx_x86_64)
        PYTHON=python
        # declare -r harddisk_sn=VB85de09d4-23402b07
        # declare -r ifmac_address=08:00:27:b0:b3:94
        declare -r harddisk_sn=FV994730S6LLF07AY
        declare -r ifmac_address=f8:ff:c2:27:00:7f
        declare -r ifip_address=$(ipconfig getifaddr en0)
        declare -r domain_name=
        ;;
    *)
        echo Unknown platform "${PLATFORM}"
        exit 1
    esac

# ======================================================================
# Initial setup, csih routines, etc.  PART 1
# ======================================================================

_csih_trace=

_csih_ERROR_STR_COLOR="\e[1;31m*** ERROR:\e[0;0m"
_csih_WARN_STR_COLOR="\e[1;33m*** Warning:\e[0;0m"
_csih_INFO_STR_COLOR="\e[1;32m*** Info:\e[0;0m"
_csih_QUERY_STR_COLOR="\e[1;35m*** Query:\e[0;0m"
_csih_STACKTRACE_STR_COLOR="\e[1;36m*** STACKTRACE:\e[0;0m"
readonly _csih_ERROR_STR_COLOR _csih_WARN_STR_COLOR
readonly _csih_INFO_STR_COLOR _csih_QUERY_STR_COLOR _csih_STACKTRACE_STR_COLOR

_csih_ERROR_STR_PLAIN="*** ERROR:"
_csih_WARN_STR_PLAIN="*** Warning:"
_csih_INFO_STR_PLAIN="*** Info:"
_csih_QUERY_STR_PLAIN="*** Query:"
_csih_STACKTRACE_STR_PLAIN="*** STACKTRACE:"
readonly _csih_ERROR_STR_PLAIN _csih_WARN_STR_PLAIN
readonly _csih_INFO_STR_PLAIN _csih_QUERY_STR_PLAIN _csih_STACKTRACE_STR_PLAIN

_csih_ERROR_STR="${_csih_ERROR_STR_COLOR}"
_csih_WARN_STR="${_csih_WARN_STR_COLOR}"
_csih_INFO_STR="${_csih_INFO_STR_COLOR}"
_csih_QUERY_STR="${_csih_QUERY_STR_COLOR}"
_csih_STACKTRACE_STR="${_csih_STACKTRACE_STR_COLOR}"

# ======================================================================
# Routine: csih_disable_color
#   Provided so that scripts which are invoked via postinstall
#   can prevent escape codes from showing up in /var/log/setup.log
# ======================================================================
csih_disable_color()
{
  _csih_ERROR_STR="${_csih_ERROR_STR_PLAIN}"
  _csih_WARN_STR="${_csih_WARN_STR_PLAIN}"
  _csih_INFO_STR="${_csih_INFO_STR_PLAIN}"
  _csih_QUERY_STR="${_csih_QUERY_STR_PLAIN}"
  _csih_STACKTRACE_STR="${_csih_STACKTRACE_STR_PLAIN}"
} # === End of csih_disable_color() === #
readonly -f csih_disable_color

# ======================================================================
# Routine: csih_stacktrace
# ======================================================================
csih_stacktrace()
{
  set +x # don''t trace this!
  local -i n=$(( ${#FUNCNAME} - 1 ))
  local val=""
  if [ -n "$_csih_trace" ]
  then
    while [ $n -gt 0 ]
    do
      if [ -n "${FUNCNAME[$n]}" ]
      then
        if [ -z "$val" ]
        then
          val="${FUNCNAME[$n]}[${BASH_LINENO[$(($n-1))]}]"
        else
          val="${val}->${FUNCNAME[$n]}[${BASH_LINENO[$(($n-1))]}]"
        fi
      fi
    n=$(($n-1))
    done
    echo -e "${_csih_STACKTRACE_STR} ${val} ${@}"
  fi
} # === End of csih_stacktrace() === #
readonly -f csih_stacktrace

# ======================================================================
# Routine: csih_trace_on
#   turns on shell tracing of csih functions
# ======================================================================
csih_trace_on()
{
  _csih_trace='set -x'
  trap 'csih_stacktrace "returning with" $?; set -x' RETURN
  set -T
  csih_stacktrace "${@}"
} # === End of csih_trace_on() === #
readonly -f csih_trace_on

# ======================================================================
# Routine: csih_trace_off
#   turns off shell tracing of csih functions
# ======================================================================
csih_trace_off()
{
  trap '' RETURN
  csih_stacktrace "${@}"
  _csih_trace=
  set +x
  set +T
} # === End of csih_trace_off() === #
readonly -f csih_trace_off

# ======================================================================
# Routine: csih_error
#   Prints the (optional) error message $1, then
#   Exits with the error code contained in $? if $? is non-zero, otherwise
#     exits with status 1
#   All other arguments are ignored
# Example: csih_error "missing file"
# NEVER RETURNS
# ======================================================================
csih_error()
{
  local errorcode=$?
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  if ((errorcode == 0))
  then
    errorcode=1
  fi
  echo -e "${_csih_ERROR_STR} ${1:-no error message provided}"
  exit ${errorcode};
} # === End of csih_error() === #
readonly -f csih_error

# ======================================================================
# Routine: csih_error_multi
#   Prints the (optional) error messages in the positional arguments, one
#     per line, and then
#   Exits with the error code contained in $? if $? is non-zero, otherwise
#     exits with status 1
#   All other arguments are ignored
# Example: csih_error_multi "missing file" "see documentation"
# NEVER RETURNS
# ======================================================================
csih_error_multi()
{
  local errorcode=$?
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  if ((errorcode == 0))
  then
    errorcode=1
  fi
  while test $# -gt 1
  do
    echo -e "${_csih_ERROR_STR} ${1}"
    shift
  done
  echo -e "${_csih_ERROR_STR} ${1:-no error message provided}"
  exit ${errorcode};
} # === End of csih_error_multi() === #
readonly -f csih_error_multi

# ======================================================================
# Routine: csih_error_recoverable
#   Prints the supplied errormessage, and propagates the $? value
# Example: csih_error_recoverable "an error message"
# ======================================================================
csih_error_recoverable()
{
  local errorcode=$?
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  echo -e "${_csih_ERROR_STR} ${1}"
  $_csih_trace
  return $errorcode
} # === End of csih_error_recoverable() === #
readonly -f csih_error_recoverable


# ======================================================================
# Routine: csih_warning
#   Prints the supplied warning message
# Example: csih_warning "replacing default file foo"
# ======================================================================
csih_warning()
{
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  echo -e "${_csih_WARN_STR} ${1}"
  $_csih_trace
} # === End of csih_warning() === #
readonly -f csih_warning

# ======================================================================
# Routine: csih_inform
#   Prints the supplied informational message
# Example: csih_inform "beginning dependency analysis..."
# ======================================================================
csih_inform()
{
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  echo -e "${_csih_INFO_STR} ${1}"
  $_csih_trace
} # === End of csih_inform() === #
readonly -f csih_inform

# ======================================================================
# Routine: csih_bug
#   Prints the supplied warning message and increase bug counter
# ======================================================================
csih_bug()
{
  let _bug_counter++
  set +x # don't trace this, but we are interested in who called
  csih_stacktrace # we'll see the arguments in the next statement
  echo -e "${_csih_WARN_STR} ${1}"
  $_csih_trace
} # === End of csih_bug() === #
readonly -f csih_bug

# ======================================================================
# Routine: next_month
#   Print next month
# ======================================================================
next_month()
{
  let -i _year=10#$(date +%Y)
  let -i _month=10#$(date +%m)
  if (( _month == 12 )) ; then
      let _year++
      let _month=1
  else
      let _month++
  fi
  if (( _month > 9 )) ; then
      month="${_month}"
  else
      month="0${_month}"
  fi
  echo -e "${_year}-${month}-01"
} # === End of next_month() === #
readonly -f next_month

# ======================================================================
# Initial setup, default values, etc.  PART 2
#
# This part of the setup has to build pyarmor test enviroments.
#
# ======================================================================

csih_inform "Python is $PYTHON"
csih_inform "Tested Package: $pkgfile"

csih_inform "Make workpath ${workpath}"
rm -rf ${workpath}
mkdir -p ${workpath} || csih_error "Make workpath FAILED"

cd ${workpath}
[[ ${pkgfile} == *.zip ]] && unzip ${pkgfile} > /dev/null 2>&1
[[ ${pkgfile} == *.tar.bz2 ]] && tar xjf ${pkgfile}
cd pyarmor-$version || csih_error "Invalid pyarmor package file"
# From pyarmor 3.5.1, main scripts are moved to src
[[ -d src ]] && mv src/* ./
# From pyarmor 5.3.3, license.lic is renamed as license.tri
[[ -f license.lic ]] || cp license.tri license.lic
tar xzf ${datafile} || csih_error "Extract data files FAILED"
cp -a ../../data/package ./ || csih_error "Copy package files FAILED"
cp ../../data/project.zip ./ && \
    cp ../../data/foo.zip ./ && \
    cp ../../data/foo-key.zip ./ || csih_error "Copy capsule files FAILED"
# From pyarmor v5.7.2, pyarmor-deprecated.py has been removed from source package
cp ../../../src/pyarmor-deprecated.py .|| csih_error "Copy pyarmor-deprecated.py FAILED"

# From pyarmor 4.5.4, platform name is renamed
if [[ -d platforms/windows32 ]] ; then
    csih_inform "Restore the name of platforms"
    (cd platforms;
        mv windows32 win32;
        mv windows64 win_amd64;
        mv linux32 linux_i386;
        mv linux64 linux_x86_64;
        mv darwin64 macosx_x86_64;)
fi

# From pyarmor 5.7.5, platform name is changed
if [[ -d platforms/windows ]] ; then
    csih_inform "Restore the name of platforms"
    (cd platforms;
        mv windows/x86 win32;
        mv windows/x86_64 win_amd64;
        mv linux/x86 linux_i386;
        mv linux/x86_64 linux_x86_64;
        mv darwin/x86_64 macosx_x86_64;)
fi

PYARMOR="$PYTHON pyarmor-deprecated.py"
[[ -f pyarmor-deprecated.py ]] || csih_error "No pyarmor-deprecated.py found"
csih_inform "PYARMOR is $PYARMOR"

csih_inform "Prepare for testing"
echo ""

# ======================================================================
# Test functions in normal license.  PART 3
#
# ======================================================================

echo ""
echo "-------------------- Start Normal License Test --------------------"
echo ""

#
# Command: capsule
#
echo ""
csih_inform "Test command: capsule"
echo ""

csih_inform "Case 1.1: show help and import pytransform"
$PYARMOR --help >result.log 2>&1 \
    || csih_bug "Case 1.1 FAILED"
[[ -f _pytransform.so ]] \
    || [[ -f _pytransform.dll ]] \
    || [[ -f _pytransform.dylib ]] \
    || csih_error "Case 1.1 FAILED: no pytransform extension found"


#
# From PyArmor 5.6, the capsule could not be generated.
#
# csih_inform "Case 1.2: generate anonymous capsule"
# $PYARMOR capsule >result.log 2>&1 \
#     || csih_bug "Case 1.2 FAILED: return non-zero code"
# [[ -f project.zip ]] \
#     || csih_bug "Case 1.2 FAILED: no project.zip found"

# csih_inform "Case 1.3: generate named capsule foo.zip"
# $PYARMOR capsule foo >result.log 2>&1 \
#     || csih_bug "Case 1.3 FAILED: return non-zero code"
# [[ -f foo.zip ]] \
#     || csih_bug "Case 1.3 FAILED: no foo.zip found"

# csih_inform "Case 1.4: generate capsule with output path"
# $PYARMOR capsule -O dist foo2 >result.log 2>&1 \
#     || csih_bug "Case 1.4 FAILED: return non-zero code"
# [[ -f dist/foo2.zip ]] \
#     || csih_bug "Case 1.4 FAILED: no dist/foo2.zip found"

# csih_inform "Case 1.5: generate capsule for next tests"
# $PYARMOR capsule foo-key >result.log 2>&1 \
#     || csih_bug "Case 1.5 FAILED: return non-zero code"
# [[ -f foo-key.zip ]] \
#     || csih_bug "Case 1.5 FAILED: no foo-key.zip found"


#
# Command: encrypt
#
echo ""
csih_inform "Test command: encrypt"
echo ""

csih_inform "Case 2.1: encrypt script"
$PYARMOR encrypt --mode=0 -C project.zip -O dist \
    foo.py >result.log 2>&1 \
    || csih_bug "Case 2.1 FAILED: return non-zero code"
[[ -f dist/foo.py${extchar} ]] \
    || csih_bug "Case 2.1 FAILED: no dist/foo.py${extchar} found"

csih_inform "Case 2.2: encrypt script with named capsule"
$PYARMOR encrypt --mode=0 --with-capsule=project.zip \
    --output=build main.py foo.py >result.log 2>&1 \
    || csih_bug "Case 2.2 FAILED: return non-zero code"
[[ -f build/main.py${extchar} ]] \
    || csih_bug "Case 2.2 FAILED: no build/main.py${extchar} found"
[[ -f build/foo.py${extchar} ]] \
    || csih_bug "Case 2.2 FAILED: no build/foo.py${extchar} found"

csih_inform "Case 2.3: encrypt script with key capsule"
$PYARMOR encrypt --mode=0 --with-capsule=foo-key.zip \
    --output=foo-key foo.py >result.log 2>&1 \
    || csih_bug "Case 2.3 FAILED: return non-zero code"
[[ -f foo-key/foo.py${extchar} ]] \
    || csih_bug "Case 2.3 FAILED: no build-key/foo.py${extchar} found"

csih_inform "Case 2.4: encrypt scripts in place"
mkdir -p test_in_place/a
cp foo.py test_in_place/foo.py
cp foo.py test_in_place/a/foo.py
echo "test_in_place/foo.py" > filelist.txt
echo "test_in_place/a/foo.py" >> filelist.txt
$PYARMOR encrypt --mode=0 --with-capsule=foo-key.zip \
    --output=foo-key -i @filelist.txt >result.log 2>&1 \
    || csih_bug "Case 2.4 FAILED: return non-zero code"
[[ -f test_in_place/foo.py${extchar} ]] || [[ -f test_in_place/a/foo.py${extchar} ]] \
    || csih_bug "Case 2.4 FAILED: no in-place encrypted foo.py${extchar} found"

csih_inform "Case 2.5: verify co_filename of code object in encrypt script"
cat <<EOF > co_hello.py
i = 1 / 0.
EOF
$PYARMOR encrypt --mode=3 -C project.zip -O test_filename co_hello.py  >result.log 2>&1
if [[ -f test_filename/co_hello.pyc ]] ; then
    cd test_filename
    cat <<EOF > main.py
import pyimcore
import co_hello
EOF
    $PYTHON main.py >result.log 2>&1
    grep -q 'File "<frozen co_hello>"' result.log || csih_bug "Case 2.5 FAILED: script name isn't right"
    cd ..
else
    csih_bug "Case 2.5 FAILED: no encrypted script found"
fi

csih_inform "Case 2.6: verify constant is obfucated"
# Generate license which disable restrict mode, "A" == 0x41
$PYARMOR license --with-capsule=project.zip -O license-no-restrict.txt "*FLAGS:A*CODE:TestCode" >result.log 2>&1
cat << EOF > co_consts.py
'''Module comment'''
title = "Hello"
def hello(arg="first"):
    '''Function comment'''
    name = "jondy"
    users = [ "bob", "time", 3]
    return "%s,%s,%s" % (name, arg, users[0])
EOF
$PYARMOR encrypt --mode=5 -C project.zip -O test_const co_consts.py >result.log 2>&1
if [[ -f test_const/co_consts.pyc ]] ; then
    cd test_const
    cp ../license-no-restrict.txt license.lic
    grep -q "\(Module comment\|Hello\|Function comment\|jondy\|bob\|time\)" co_consts.pyc \
        && csih_bug "Case 2.6 FAILED: co_consts still in clear text"
    cat <<EOF > main.py
import pyimcore
import sys
import co_consts
sys.stdout.write("%s:%s:%s" % (co_consts.title, co_consts.__doc__, co_consts.hello("second")))
EOF
    $PYTHON main.py >result.log 2>&1 || csih_bug "Case 2.6 FAILED: run script return non-zero code"
    grep -q "Hello:Module comment:jondy,second,bob" result.log \
        || csih_bug "Case 2.6 FAILED: python script returns unexpected result"
    cd ..
else
    csih_bug "Case 2.6 FAILED: no test_consts/co_consts.pyc found"
fi

csih_inform "Case 2.7: verify mode 6 works"
$PYARMOR encrypt --mode=6 -C project.zip -O test_mode6 co_consts.py >result.log 2>&1
if [[ -f test_mode6/co_consts.pyc ]] ; then
    cd test_mode6
    cp ../license-no-restrict.txt license.lic
    grep -q "\(Module comment\|Hello\|Function comment\|jondy\|time\)" co_consts.pyc \
        && csih_bug "Case 2.7 FAILED: co_consts still in clear text"
    cat <<EOF > main.py
import pyimcore
import sys
import co_consts
sys.stdout.write("%s:%s:%s" % (co_consts.title, co_consts.__doc__, co_consts.hello("second")))
EOF
    $PYTHON main.py >result.log 2>&1 || csih_bug "Case 2.7 FAILED: run script return non-zero code"
    grep -q "Hello:Module comment:jondy,second,bob" result.log \
        || csih_bug "Case 2.7 FAILED: python script returns unexpected result"
    cd ..
else
    csih_bug "Case 2.7 FAILED: no test_mode6/co_consts.pyc found"
fi

csih_inform "Case 2.8: verify mode 7 works"
$PYARMOR encrypt --mode=7 -C project.zip -O test_mode7 co_consts.py >result.log 2>&1
if [[ -f test_mode7/co_consts.py ]] ; then
    cd test_mode7
    cp ../license-no-restrict.txt license.lic
    grep -q "\(Module comment\|Hello\|Function comment\|jondy\|bob\|time\)" co_consts.py \
        && csih_bug "Case 2.8 FAILED: co_consts still in clear text"
    cat <<EOF > main.py
import pyimcore
import sys
import co_consts
sys.stdout.write("%s:%s:%s" % (co_consts.title, co_consts.__doc__, co_consts.hello("second")))
EOF
    $PYTHON main.py >result.log 2>&1 || csih_bug "Case 2.8 FAILED: run script return non-zero code"
    grep -q "Hello:Module comment:jondy,second,bob" result.log \
        || csih_bug "Case 2.8 FAILED: python script returns unexpected result"
    cd ..
else
    csih_bug "Case 2.8 FAILED: no test_mode8/co_consts.py found"
fi

csih_inform "Case 2.9: verify mode 8 works"
$PYARMOR encrypt --mode=8 -C project.zip -O test_mode8 co_consts.py >result.log 2>&1
if [[ -f test_mode8/co_consts.py ]] ; then
    cd test_mode8
    cp ../license-no-restrict.txt license.lic
    grep -q "\(Module comment\|Hello\|Function comment\|jondy\|bob\|time\)" co_consts.py \
        && csih_bug "Case 2.9 FAILED: co_consts still in clear text"
    cat <<EOF > main.py
import pyimcore
import sys
import co_consts
sys.stdout.write("%s:%s:%s" % (co_consts.title, co_consts.__doc__, co_consts.hello("second")))
EOF
    $PYTHON main.py >result.log 2>&1 || csih_bug "Case 2.9 FAILED: run script return non-zero code"
    grep -q "Hello:Module comment:jondy,second,bob" result.log \
        || csih_bug "Case 2.9 FAILED: python script returns unexpected result"
    cd ..
else
    csih_bug "Case 2.9 FAILED: no test_mode8/co_consts.py found"
fi

csih_inform "Case 2.10: obfuscate empty script with mode 7"
cat <<EOF > empty.py
EOF
$PYARMOR encrypt --mode=7 -C project.zip -O test_mode7 empty.py >result.log 2>&1
if [[ ! -f test_mode7/empty.py ]] ; then
    csih_bug "Case 2.10 FAILED: no test_mode7/empty.py found"
fi

csih_inform "Case 2.11: obfuscate empty script with mode 8"
$PYARMOR encrypt --mode=8 -C project.zip -O test_mode8 empty.py >result.log 2>&1
if [[ ! -f test_mode8/empty.py ]] ; then
    csih_bug "Case 2.11 FAILED: no test_mode8/empty.py found"
fi

csih_inform "Case 2.12: test main script with mode 8"
cp empty.py empty2.py
$PYARMOR encrypt --mode=8 -C project.zip -O test_mode8 -m empty2 empty2.py >result.log 2>&1
if [[ -f test_mode8/empty2.py ]] ; then
    grep -q "import pyimcore" test_mode8/empty2.py || csih_bug "Case 2.12 FAILED: no main entry generated"
else
    csih_bug "Case 2.12 FAILED: no test_mode8/empty2.py found"
fi

csih_inform "Case 2.13: test obfuscate scripts with mode 9, 10, 11, 12, 13, 14"
for mode in 9 10 11 12 13 14 ; do
  $PYARMOR encrypt --mode=$mode -C project.zip -O test_mode$mode foo.py >result.log 2>&1
  if [[ -f test_mode${mode}/foo.py ]] ; then
      grep -q "__pyarmor__" test_mode${mode}/foo.py \
          || csih_bug "Case 2.13 FAILED: no __pyarmor__ found in obfuscated script for mode $mode"
  else
      csih_bug "Case 2.13 FAILED: no test_mode${mode}/foo.py found"
  fi
done

#
# Import encrypted module and run encrypted scripts
#
echo ""
csih_inform "Test import and run encrypted scripts"
echo ""

csih_inform "Case 3.1: import encrypted module"
(cd dist ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.1 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.1 FAILED: python script returns unexpected result"

csih_inform "Case 3.1T: import encrypted module in other thread"
cat <<EOF > dist/t_startup.py
import sys
import pyimcore
import foo
import threading
def target():
    sys.stderr.write("foo.hello(2) = %d\n" % foo.hello(2))
threading.Thread(target=target).start()
EOF
(cd dist ;
    $PYTHON t_startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.1T FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.1T FAILED: python script returns unexpected result"

csih_inform "Case 3.2: run encrypted script"
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 3.2 FAILED: return non-zero code"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 3.2 FAILED: python script returns unexpected result"

csih_inform "Case 3.3: import encrypted module with module key"
(cd foo-key ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.3 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.3 FAILED: python script returns unexpected result"

csih_inform "Case 3.4: run encrypted code from __future__"
echo "from __future__ import with_statement" > foo-future.py
cat foo.py >> foo-future.py
$PYARMOR encrypt --mode=0 --with-capsule=foo-key.zip \
    --output=foo-future foo-future.py >result.log 2>&1 \
    || csih_bug "Case 3.4 FAILED: return non-zero code"
(cd foo-future ;
    cp ../startup.py ./ ;
    mv foo-future.pye foo.pye ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.4 FAILED: return non-zero code"
)

csih_inform "Case 3.5: import encrypted code with mode 1"
$PYARMOR encrypt --with-capsule=project.zip --mode=1 \
    --output=build_m1 foo.py >result.log 2>&1 \
    || csih_bug "Case 3.5 FAILED: return non-zero code"
(cd build_m1 ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.5 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.5 FAILED: python script returns unexpected result"


csih_inform "Case 3.6: import encrypted code with mode 2"
$PYARMOR encrypt --with-capsule=project.zip --mode=2 \
    --output=build_m2 foo.py >result.log 2>&1 \
    || csih_bug "Case 3.6 FAILED: return non-zero code"
(cd build_m2 ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.6 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.6 FAILED: python script returns unexpected result"

csih_inform "Case 3.7: import encrypted package"
$PYARMOR encrypt --mode=0 --with-capsule=project.zip --in-place \
    --output=build_pkg package/*.py >result.log 2>&1 \
    || csih_bug "Case 3.7 FAILED: return non-zero code"
(cp -a package build_pkg;
    cd build_pkg && rm package/*.py ;
    cp ../startup.py ./ ;
    sed -i -e 's/import foo/from package import foo/g' startup.py ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.7 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.7 FAILED: python script returns unexpected result"

csih_inform "Case 3.8: import encrypted code with mode 3"
$PYARMOR encrypt --with-capsule=project.zip --mode=3 \
    --output=build_m3 foo.py >result.log 2>&1 \
    || csih_bug "Case 3.8 FAILED: return non-zero code"
(cd build_m3 ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.8 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case 3.8 FAILED: python script returns unexpected result"


csih_inform "Case 3.9: run encrypted code with mode 3"
$PYARMOR encrypt --with-capsule=project.zip --mode=3 \
    --output=build_m3a -m main:start.py main.py foo.py >result.log 2>&1 \
    || csih_bug "Case 3.9 FAILED: return non-zero code"
(cd build_m3a ;
    $PYTHON start.py >../result.log 2>&1 \
        || csih_bug "Case 3.9 FAILED: return non-zero code"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 3.9 FAILED: python script returns unexpected result"

#
# Cross publish
#
echo ""
csih_inform "Test cross publish"
echo ""

csih_inform "Case 4.1: cross publish for windows"
$PYARMOR encrypt --mode=0 \
    --output=others \
    --plat-name=win_amd64 \
    foo.py  >result.log 2>&1 \
    || csih_bug "Case 4.1 FAILED: return non-zero code"
[[ -f others/foo.py${extchar} ]] \
    || csih_bug "Case 4.1 FAILED: no others/foo.py${extchar} found"
[[ -f others/_pytransform.dll ]] \
    || csih_bug "Case 4.1 FAILED: no others/_pytransform.dll found"

csih_inform "Case 4.2: cross publish for linux"
$PYARMOR encrypt --mode=0 \
    --output=others \
    --plat-name=linux_x86_64 \
    main.py  >result.log 2>&1 \
    || csih_bug "Case 4.2 FAILED: return non-zero code"
[[ -f others/main.py${extchar} ]] \
    || csih_bug "Case 4.2 FAILED: no others/main.py${extchar} found"
[[ -f others/_pytransform.so ]] \
    || csih_bug "Case 4.2 FAILED: no others/_pytransform.so found"

#
# Command: license
#
echo ""
csih_inform "Test command: license"
echo ""

csih_inform "Case 5.1: generate license"
$PYARMOR license --with-capsule=project.zip \
    -O license.txt TESTCODE >result.log 2>&1 \
    || csih_bug "Case 5.1 FAILED: return non-zero code"
[[ -f license.txt ]] \
    || csih_bug "Case 5.1 FAILED: no license.txt found"
cp license.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.1 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.1 FAILED: python script returns unexpected result"

csih_inform "Case 5.2: generate license bind to fixed machine"
$PYARMOR license --with-capsule=project.zip \
    --bind-disk="${harddisk_sn}" -O license.txt >result.log 2>&1 \
    || csih_bug "Case 5.2 FAILED: return non-zero code"
[[ -f license.txt ]] \
    || csih_bug "Case 5.2 FAILED: no license.txt found"
cp license.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.2 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.2 FAILED: python script returns unexpected result"

csih_inform "Case 5.3: generate period license bind to fixed machine"
$PYARMOR license --with-capsule=project.zip -e $(next_month) \
    --bind-disk="${harddisk_sn}" -O license1.txt >result.log 2>&1 \
    || csih_bug "Case 5.3 FAILED: return non-zero code"
[[ -f license1.txt ]] \
    || csih_bug "Case 5.3 FAILED: no license.txt found"
cp license1.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.3 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.3 FAILED: python script returns unexpected result"

csih_inform "Case 5.4: generate expired license"
$PYARMOR license --with-capsule=project.zip -e 2014-01-01 \
    -O license2.txt whoami@unknown.com >result.log 2>&1 \
    || csih_bug "Case 5.4 FAILED: return non-zero code"
[[ -f license2.txt ]] \
    || csih_bug "Case 5.4 FAILED: no license.txt found"
cp license2.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        && csih_bug "Case 5.4 FAILED: return zero code when license is expired"
)
grep -q "License is expired" result.log \
    || csih_bug "Case 5.4 FAILED: expired license still work"

csih_inform "Case 5.5: generate bind file license"
$PYARMOR license --with-capsule=project.zip --bind-file id_rsa \
    -O license3.txt my_id_rsa >result.log 2>&1 \
    || csih_bug "Case 5.5 FAILED: return non-zero code"
[[ -f license3.txt ]] \
    || csih_bug "Case 5.5 FAILED: no license.txt found"
cp license3.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    cp ../id_rsa my_id_rsa ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.5 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.5 FAILED: python script returns unexpected result"

csih_inform "Case 5.6: generate bind file license with expired date"
$PYARMOR license --with-capsule=project.zip -e $(next_month) \
    --bind-file id_rsa -O license4.txt my_id_rsa >result.log 2>&1 \
    || csih_bug "Case 5.6 FAILED: return non-zero code"
[[ -f license4.txt ]] \
    || csih_bug "Case 5.6 FAILED: no license.txt found"
cp license4.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    cp ../id_rsa my_id_rsa ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.6 FAILED: return zero code when license is expired"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.6 FAILED: python script returns unexpected result"

csih_inform "Case 5.7: generate license bind to mac address"
$PYARMOR license --with-capsule=project.zip \
    --bind-mac="${ifmac_address}" -O license-ifmac.txt >result.log 2>&1 \
    || csih_bug "Case 5.7 FAILED: return non-zero code"
[[ -f license-ifmac.txt ]] \
    || csih_bug "Case 5.7 FAILED: no license-ifmac.txt found"
cp license-ifmac.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.7 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.7 FAILED: python script returns unexpected result"

csih_inform "Case 5.7-1: generate license bind to other mac address"
$PYARMOR license --with-capsule=project.zip \
    --bind-mac="xx:yy" -O license-ifmac2.txt >result.log 2>&1 \
    || csih_bug "Case 5.7-1 FAILED: return non-zero code"
[[ -f license-ifmac2.txt ]] \
    || csih_bug "Case 5.7-1 FAILED: no license-ifmac2.txt found"
cp license-ifmac2.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        && csih_bug "Case 5.7-1 FAILED: return 0 when run script by invalid license"
)
grep -q "License is not for this machine" result.log \
    || csih_bug "Case 5.7-1 FAILED: no failed message found"

csih_inform "Case 5.8: generate license bind to ip address"
$PYARMOR license --with-capsule=project.zip \
    --bind-ip="${ifip_address}" -O license-ifip.txt >result.log 2>&1 \
    || csih_bug "Case 5.8 FAILED: return non-zero code"
[[ -f license-ifip.txt ]] \
    || csih_bug "Case 5.8 FAILED: no license-ifip.txt found"
cp license-ifip.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.8 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.8 FAILED: python script returns unexpected result"

csih_inform "Case 5.8-1: generate license bind to other ip address"
$PYARMOR license --with-capsule=project.zip \
    --bind-ip="192.188.2.2" -O license-ifip2.txt >result.log 2>&1 \
    || csih_bug "Case 5.8-1 FAILED: return non-zero code"
[[ -f license-ifip2.txt ]] \
    || csih_bug "Case 5.8-1 FAILED: no license-ifip2.txt found"
cp license-ifip2.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        && csih_bug "Case 5.8-1 FAILED: return 0 when run script by invalid license"
)
grep -q "License is not for this machine" result.log \
    || csih_bug "Case 5.8-1 FAILED: no failed message found"

csih_inform "Case 5.8-2: generate license bind to both mac and ip address"
$PYARMOR license --with-capsule=project.zip \
    --bind-mac="${ifmac_address}" --bind-ip="${ifip_address}" -O license-macip.txt >result.log 2>&1 \
    || csih_bug "Case 5.8-2 FAILED: return non-zero code"
[[ -f license-macip.txt ]] \
    || csih_bug "Case 5.8-2 FAILED: no license-macip.txt found"
cp license-macip.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        || csih_bug "Case 5.8-2 FAILED: return non-zero code when run script"
)
grep -q "Result is 10" result.log \
    || csih_bug "Case 5.8-2 FAILED: python script returns unexpected result"

csih_inform "Case 5.9-1: generate license bind to other domain name"
$PYARMOR license --with-capsule=project.zip \
    --bind-domain="snsoffice.com" -O license-domain2.txt >result.log 2>&1 \
    || csih_bug "Case 5.9-1 FAILED: return non-zero code"
[[ -f license-domain2.txt ]] \
    || csih_bug "Case 5.9-1 FAILED: no license-domain.txt found"
cp license-domain2.txt build/license.lic
(cd build ;
    cp ../bootstrap.py ./ ;
    $PYTHON bootstrap.py >../result.log 2>&1 \
        && csih_bug "Case 5.9-1 FAILED: return 0 when run script by invalid license"
)
grep -q "License is not for this machine" result.log \
    || csih_bug "Case 5.9-1 FAILED: no failed message found"

#
# AST/PYC Hole
#
echo ""
csih_inform "Test crack: ast node / pyc"
echo ""

$PYARMOR encrypt --mode=0 --with-capsule=project.zip \
    --output=hole sky.py >result.log 2>&1 \
    || csih_bug "Case 6 FAILED: return non-zero code"
[[ -f hole/sky.py${extchar} ]] \
    || csih_bug "Case 6 FAILED: no hole/sky.py${extchar} found"

csih_inform "Case 6.1: run encrypted func_code"
(cd hole ;
    echo "import pyimcore
import pytransform
pytransform.exec_file('sky.py${extchar}')" > startup.py ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 6.1 FAILED: return non-zero code"
)
grep -q "star 3 is 9" result.log \
    || csih_bug "Case 6.1 FAILED: can not run encrypted func_code"

csih_inform "Case 6.2: crack encrypted func_code"
(cd hole ;
    cp ../sky.py ./sky2.py ;
    cp ../hole.py ./;
    $PYTHON hole.py >../result.log 2>&1 \
        || csih_bug "Case 6.2 FAILED: return non-zero code"
)
grep -q "OK" result.log \
    || csih_bug "Case 6.2 FAILED: find hole to get bytecode"

csih_inform "Remove files/dirs"
rm -rf dist build others hole project.zip foo.zip

echo ""
echo "-------------------- End Normal License Test --------------------"
echo ""


# ======================================================================
# Test functions in trial license.  PART 4
#
# DEPRECATED from v5.6.0, no capsule could be generated
# ======================================================================

# echo ""
# echo "-------------------- Start Trial License Test --------------------"
# echo ""

# csih_inform "Replace normal license with trial license"
# cp license.tri license.lic

# csih_inform "Case T1.1: generate capsule in trial license"
# $PYARMOR capsule >result.log 2>&1 \
#     || csih_bug "Case T1.1 FAILED: return non-zero code"
# [[ -f project.zip ]] \
#     || csih_bug "Case T1.1 FAILED: no project.zip found"

# csih_inform "Case T1.2: encrypt script in trial license"
# $PYARMOR encrypt --mode=0 -C project.zip -O dist foo.py >result.log 2>&1 \
#     || csih_bug "Case T1.2 FAILED: return non-zero code"
# [[ -f dist/foo.py${extchar} ]] \
#     || csih_bug "Case T1.2 FAILED: no dist/foo.py${extchar} found"

# csih_inform "Case T1.3: import encrypted module in trial license"
# (cd dist ;
#     cp ../startup.py ./ ;
#     $PYTHON startup.py >../result.log 2>&1 \
#         || csih_bug "Case T1.3 FAILED: return non-zero code"
# )
# grep -q "foo.hello(2) = 7" result.log \
#     || csih_bug "Case T1.3 FAILED: python script returns unexpected result"

# csih_inform "Remove files/dirs: dist build others project.zip foo.zip"
# rm -rf dist build others project.zip foo.zip

# echo ""
# echo "-------------------- End Trial License Test --------------------"
# echo ""


# ======================================================================
# Test functions in expired trial license.  PART 5
#
# DEPRECATED from v4.6.1, no trial license
#
# ======================================================================
# echo ""
# echo "-------------------- Start Expired License Test --------------------"
# echo ""

# csih_inform "Replace trial license with expired trial license"
# cp expired-license.tri license.lic

# searchmsg="Check trial license failed"

# csih_inform "Case E1.1: generate capsule in expired license"
# rm -rf _pytransform.dll _pytransform.so _pytransform.dylib
# $PYARMOR capsule foo >result.log 2>&1 \
#     && csih_bug "Case E1.1 FAILED: return zero code"
# grep -q "$searchmsg" result.log \
#     || csih_bug "Case E1.1 FAILED: unexpected message"

# csih_inform "Case E1.2: encrypt script in expired license"
# rm -rf _pytransform.dll _pytransform.so _pytransform.dylib
# $PYARMOR encrypt --mode=0 -O dist foo.py >result.log 2>&1 \
#     && csih_bug "Case E1.2 FAILED: return zero code"
# grep -q "$searchmsg" result.log \
#     || csih_bug "Case E1.2 FAILED: unexpected message"

# echo ""
# echo "-------------------- End Expired License Test --------------------"
# echo ""

# return test root
cd ../..

echo "------------------------------------------------------------------"
echo ""
csih_inform "Test finished for ${PYTHON}"
(( ${_bug_counter} == 0 )) || csih_error "${_bug_counter} bugs found"
echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ${workpath} \
&& csih_inform "Congratulations, there is no bug found"

echo ""
echo "------------------------------------------------------------------"
echo ""
