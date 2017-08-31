#! /bin/bash

UNAME=$(uname)
if [[ ${UNAME:0:5} == Linux ]] ; then
    if [[ $(arch) == x86_64 ]] ; then
        PLATFORM=linux_x86_64
    else
        PLATFORM=linux_i386
    fi
    PKGEXT=bz2
else
    if [[ $(ARCH) == amd64 ]] ; then
        PLATFORM=win_amd64
    else
        PLATFORM=win32
    fi
    PKGEXT=zip
fi

# version=${1:-2.6.1}
filename=$(cd ../src/dist; ls -t pyarmor-*.${PKGEXT}) || exit 1
version=${filename:8:5}
extchar=${PYARMOR_EXTRA_CHAR:-e}

case ${PLATFORM} in

    win32)
        PYTHON=${PYTHON:-C:/Python26/python}
        workpath=/cygdrive/d/projects/pyarmor/tests/__runtest__
        datafile=/cygdrive/d/projects/pyarmor/tests/data/pyarmor-data.tar.gz
        pkgfile=/cygdrive/d/projects/pyarmor/src/dist/pyarmor-$version.${PKGEXT}
        declare -r harddisk_sn=100304PBN2081SF3NJ5T
        ;;
    win_amd64)
        ;;
    linux_i386)
        ;;
    linux_x86_64)
        PYTHON=python
        workpath=~/workspace//pyarmor/tests/__runtest__
        datafile=~/workspace//pyarmor/tests/data/pyarmor-data.tar.gz
        pkgfile=~/workspace/pyarmor/src/dist/pyarmor-$version.${PKGEXT}
        declare -r harddisk_sn='            9WK3FEMQ'
        ;;
    *)
        echo Unknown platform "${PLATFORM}"
        exit 1
    esac
declare -i _bug_counter=0

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
  month="0${_month}"
  echo -e "${_year}-${month:-1:2}-01"
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
tar xzf ${datafile} || csih_error "Extract data files FAILED"

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
$PYTHON pyarmor.py --help >result.log 2>&1 \
    || csih_bug "Case 1.1 FAILED"
[[ -f _pytransform.so ]] \
    || [[ -f _pytransform.dll ]] \
    || csih_error "Case 1.1 FAILED: no pytransform extension found"

csih_inform "Case 1.2: generate anonymous capsule"
$PYTHON pyarmor.py capsule  >result.log 2>&1 \
    || csih_bug "Case 1.2 FAILED: return non-zero code"
[[ -f project.zip ]] \
    || csih_bug "Case 1.2 FAILED: no project.zip found"

csih_inform "Case 1.3: generate named capsule foo.zip"
$PYTHON pyarmor.py capsule foo >result.log 2>&1 \
    || csih_bug "Case 1.3 FAILED: return non-zero code"
[[ -f foo.zip ]] \
    || csih_bug "Case 1.3 FAILED: no foo.zip found"

csih_inform "Case 1.4: generate capsule with output path"
$PYTHON pyarmor.py capsule -O dist foo2 >result.log 2>&1 \
    || csih_bug "Case 1.4 FAILED: return non-zero code"
[[ -f dist/foo2.zip ]] \
    || csih_bug "Case 1.4 FAILED: no dist/foo2.zip found"

csih_inform "Case 1.5: generate capsule for next tests"
$PYTHON pyarmor.py capsule foo-key >result.log 2>&1 \
    || csih_bug "Case 1.5 FAILED: return non-zero code"
[[ -f foo-key.zip ]] \
    || csih_bug "Case 1.5 FAILED: no foo-key.zip found"

#
# Command: encrypt
#
echo ""
csih_inform "Test command: encrypt"
echo ""

csih_inform "Case 2.1: encrypt script"
$PYTHON pyarmor.py encrypt -C project.zip -O dist \
    foo.py >result.log 2>&1 \
    || csih_bug "Case 2.1 FAILED: return non-zero code"
[[ -f dist/foo.py${extchar} ]] \
    || csih_bug "Case 2.1 FAILED: no dist/foo.py${extchar} found"

csih_inform "Case 2.2: encrypt script with named capsule"
$PYTHON pyarmor.py encrypt --with-capsule=project.zip \
    --output=build main.py foo.py >result.log 2>&1 \
    || csih_bug "Case 2.2 FAILED: return non-zero code"
[[ -f build/main.py${extchar} ]] \
    || csih_bug "Case 2.2 FAILED: no build/main.py${extchar} found"
[[ -f build/foo.py${extchar} ]] \
    || csih_bug "Case 2.2 FAILED: no build/foo.py${extchar} found"

csih_inform "Case 2.3: encrypt script with key capsule"
$PYTHON pyarmor.py encrypt --with-capsule=foo-key.zip \
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
$PYTHON pyarmor.py encrypt --with-capsule=foo-key.zip \
    --output=foo-key -i @filelist.txt >result.log 2>&1 \
    || csih_bug "Case 2.4 FAILED: return non-zero code"
[[ -f test_in_place/foo.py${extchar} ]] || [[ -f test_in_place/a/foo.py${extchar} ]] \
    || csih_bug "Case 2.4 FAILED: no in-place encrypted foo.py${extchar} found"

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
$PYTHON pyarmor.py encrypt --with-capsule=foo-key.zip \
    --output=foo-future foo-future.py >result.log 2>&1 \
    || csih_bug "Case 3.4 FAILED: return non-zero code"
(cd foo-future ;
    cp ../startup.py ./ ;
    mv foo-future.pye foo.pye ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case 3.4 FAILED: return non-zero code"
)


#
# Cross publish
#
echo ""
csih_inform "Test cross publish"
echo ""

csih_inform "Case 4.1: cross publish for windows"
$PYTHON pyarmor.py encrypt \
    --output=others \
    --plat-name=win_amd64 \
    foo.py  >result.log 2>&1 \
    || csih_bug "Case 4.1 FAILED: return non-zero code"
[[ -f others/foo.py${extchar} ]] \
    || csih_bug "Case 4.1 FAILED: no others/foo.py${extchar} found"
[[ -f others/_pytransform.dll ]] \
    || csih_bug "Case 4.1 FAILED: no others/_pytransform.dll found"

csih_inform "Case 4.2: cross publish for linux"
$PYTHON pyarmor.py encrypt \
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
$PYTHON pyarmor.py license --with-capsule=project.zip \
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
$PYTHON pyarmor.py license --with-capsule=project.zip \
    --bind-disk -O license.txt 100304PBN2081SF3NJ5T >result.log 2>&1 \
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
$PYTHON pyarmor.py license --with-capsule=project.zip -e $(next_month) \
    --bind-disk -O license1.txt ${harddisk_sn} >result.log 2>&1 \
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
$PYTHON pyarmor.py license --with-capsule=project.zip -e 2014-01-01 \
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
grep -q "Verify license failed" result.log \
    || csih_bug "Case 5.4 FAILED: expired license still work"

csih_inform "Case 5.5: generate bind file license"
$PYTHON pyarmor.py license --with-capsule=project.zip --bind-file id_rsa \
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
$PYTHON pyarmor.py license --with-capsule=project.zip -e $(next_month) \
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

#
# AST/PYC Hole
#
echo ""
csih_inform "Test crack: ast node / pyc"
echo ""

$PYTHON pyarmor.py encrypt --with-capsule=project.zip \
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
# ======================================================================

echo ""
echo "-------------------- Start Trial License Test --------------------"
echo ""

csih_inform "Replace normal license with trial license"
cp license.tri license.lic

csih_inform "Case T1.1: generate capsule in trial license"
$PYTHON pyarmor.py capsule >result.log 2>&1 \
    || csih_bug "Case T1.1 FAILED: return non-zero code"
[[ -f project.zip ]] \
    || csih_bug "Case T1.1 FAILED: no project.zip found"

csih_inform "Case T1.2: encrypt script in trial license"
$PYTHON pyarmor.py encrypt -C project.zip -O dist foo.py >result.log 2>&1 \
    || csih_bug "Case T1.2 FAILED: return non-zero code"
[[ -f dist/foo.py${extchar} ]] \
    || csih_bug "Case T1.2 FAILED: no dist/foo.py${extchar} found"

csih_inform "Case T1.3: import encrypted module in trial license"
(cd dist ;
    cp ../startup.py ./ ;
    $PYTHON startup.py >../result.log 2>&1 \
        || csih_bug "Case T1.3 FAILED: return non-zero code"
)
grep -q "foo.hello(2) = 7" result.log \
    || csih_bug "Case T1.3 FAILED: python script returns unexpected result"

csih_inform "Remove files/dirs: dist build others project.zip foo.zip"
rm -rf dist build others project.zip foo.zip

echo ""
echo "-------------------- End Trial License Test --------------------"
echo ""

# ======================================================================
# Test functions in expired trial license.  PART 5
#
# ======================================================================
echo ""
echo "-------------------- Start Expired License Test --------------------"
echo ""

csih_inform "Replace trial license with expired trial license"
cp expired-license.tri license.lic

searchmsg="Check trial license failed"

csih_inform "Case E1.1: generate capsule in expired license"
rm -rf _pytransform.dll _pytransform.so
$PYTHON pyarmor.py capsule foo >result.log 2>&1 \
    && csih_bug "Case E1.1 FAILED: return zero code"
grep -q "$searchmsg" result.log \
    || csih_bug "Case E1.1 FAILED: unexpected message"

csih_inform "Case E1.2: encrypt script in expired license"
rm -rf _pytransform.dll _pytransform.so
$PYTHON pyarmor.py encrypt -O dist foo.py >result.log 2>&1 \
    && csih_bug "Case E1.2 FAILED: return zero code"
grep -q "$searchmsg" result.log \
    || csih_bug "Case E1.2 FAILED: unexpected message"

echo ""
echo "-------------------- End Expired License Test --------------------"
echo ""


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
