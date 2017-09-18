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
    if [[ $(arch) == x86_64 ]] ; then
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
workpath=__runtest__
datafile=$(pwd)/data/pyarmor-data.tar.gz
testfile=$(pwd)/data/pybench
pkgfile=$(pwd)/../src/dist/pyarmor-${version}.${PKGEXT}
resultpath=../../../data

case ${PLATFORM} in

    win32)
        PYTHON=${PYTHON:-C:/Python32/python}
        ;;
    win_amd64)
        PYTHON=${PYTHON:-C:/Python26/python}
        ;;
    linux_i386)
        PYTHON=${PYTHON:-python}
        ;;
    linux_x86_64)
        PYTHON=${PYTHON:-python}
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
cp -a ${testfile} ./ || csih_error "Copy pybench files FAILED"

pyver=$("$PYTHON" -c"import sys
sys.stdout.write('%d%d' % sys.version_info[:2])")

csih_inform "Prepare for testing"
echo ""

# ======================================================================
# Test functions.  PART 3
#
# ======================================================================

echo ""
echo "-------------------- Start Test --------------------"
echo ""

csih_inform "* Generate capsule"
$PYTHON pyarmor.py capsule project >result.log 2>&1 \
    || csih_error "Return non-zero code"
[[ -f project.zip ]] \
    || csih_error "No project.zip found"

output=dist
mode=0
result_base=../py${pyver}.base.bench

csih_inform "* Run plain pybench"
(cd pybench; $PYTHON pybench.py -f ${result_base})
csih_inform "* Write result to ${result_base}"

for mode in 0 1 2 ; do

  result_mode=../py${pyver}.mode${mode}.bench
  result=${resultpath}/py${pyver}.base-mode${mode}.bench
  
  echo ""
  echo "-------------------- Mode ${mode} --------------------"
  echo ""
  
  csih_inform "* Encrypt package pybench"
  rm -rf ${output}
  cp -a pybench/ ${output}/
  if [[ ${pyver:0:1} == "3" ]] ; then
      sed -i -e"s/u'/'/g" ${output}/Unicode.py
  fi
  $PYTHON pyarmor.py encrypt -C project.zip -O ${output} --in-place \
      ${output}/*.py ${output}/package/*.py >result.log 2>&1 \
      || csih_error "FAILED: return non-zero code"
  [[ -f ${output}/pybench.py${extchar} ]] \
      || csih_error "FAILED: no ${output}/pybench/pybench.py${extchar} found"
  find ${output}/ -name "*.py" -delete
  
  csih_inform "* Generate main wrapper"
  $PYTHON pyarmor.py encrypt -C project.zip -O ${output} -m pybench >result.log 2>&1 \
      || csih_error "FAILED: return non-zero code"
  [[ -f ${output}/pybench.py ]] \
      || csih_error "FAILED: no wrapper ${output}/pybench/pybench.py} found"
  mv ${output}/{pybench.py,main.py}
  
  csih_inform "* Run encrypted pybench"
  (cd ${output}; $PYTHON main.py -v -f ${result_mode} >result.log 2>&1) \
      || csih_error "FAILED: return non-zero code"
  csih_inform "* Write result to ${result_mode}"
  
  csih_inform "* Compare pybench result"
  (cd pybench; $PYTHON pybench.py -s ${result_base} -c ${result_mode} > ${result}) \
      || csih_error "FAILED: return non-zero code"
  csih_inform "* Write result to ${result}"
done

echo ""
echo "------------------------------------------------------------------"
echo ""
csih_inform "Test finished for ${PYTHON}"

echo "" && \
csih_inform "Remove workpath ${workpath}" \
&& echo "" \
&& rm -rf ../../${workpath}

echo ""
echo "------------------------------------------------------------------"
echo ""
