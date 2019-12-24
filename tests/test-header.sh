#! /bin/bash

SED=sed
UNAME=$(uname)
if [[ ${UNAME:0:5} == Linux ]] ; then
    if [[ $(arch) == x86_64 ]] ; then
        PLATFORM=linux_x86_64
    else
        PLATFORM=linux_i386
    fi
    PKGEXT=tar.bz2
    DLLEXT=.so
    ARMOR=./pyarmor
else

    if [[ $(uname) == Darwin ]] ; then
        PLATFORM=macosx_x86_64
        PKGEXT=tar.bz2
        DLLEXT=.dylib
        ARMOR=./pyarmor
        SED=gsed
    else
        if [[ $(arch) == x86_64 ]] ; then
            PLATFORM=win_amd64
        else
            PLATFORM=win32
        fi
        PKGEXT=zip
        DLLEXT=.dll
        ARMOR=./pyarmor.bat
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
workpath=__runtest2__
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
        PYTHON=${PYTHON:-python}
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
# csih routines
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
# Routine: check_file_exists
#   Write a bug if file doesn't exists
# Example: check_file_exists dist/foo.py
# ======================================================================
check_file_exists()
{
  [[ -f "$1" ]] || csih_bug "no $1 found"
}

# ======================================================================
# Routine: check_file_not_exists
#   Write a bug if file exists
# Example: check_file_not_exists dist/foo.py
# ======================================================================
check_file_not_exists()
{
  [[ -f "$1" ]] && csih_bug "unexpected $1 found"
}

# ======================================================================
# Routine: check_file_content
#   Write a bug if file doesn't include some content
# Example: check_file_content result.log "__pyarmor__"
# ======================================================================
check_file_content()
{
    if [[ "$3" == "not" ]] ; then
        grep -q "$2" "$1" && csih_bug "'$2' found in '$1'"
    else
        grep -q "$2" "$1" || csih_bug "'$2' not found in '$1'"
    fi
}

# ======================================================================
# Routine: check_return_value
#   Write a bug  if return value is not 0
# Example: check_return_value
# ======================================================================
check_return_value()
{
    (( $? )) && csih_bug "command return non-zero value"
}

# ======================================================================
# Routine: check_python_version_for_auto_wrap_mode
#   Return 0 if auto wrap mode doesn't work in this version
# Example:
#   check_python_version_for_auto_wrap_mode && echo "No auto wrap"
#   if ! check_python_version_for_auto_wrap_mode ; then
#     echo "Auto wrap mode works"
#   fi
# ======================================================================
check_python_version_for_auto_wrap_mode()
{
    # unused, now all python versions work in auto-wrap mode
    $PYTHON --version 2>&1 \
        | grep -q "\(Python 3.0\|Python 3.1\|Python 3.2\)" \
        && csih_inform "The auto wrap mode doesn't work for $PYTHON"
}

# ======================================================================
# Routine: patch_cross_protection_code_for_python3.0
#
#   Remove "assert_buildin(open)" from cross protection code if python
#   version is 3.0, because it return OpenWrapper in Python3.0
# ======================================================================
patch_cross_protection_code_for_python3.0()
{
    $PYTHON --version 2>&1 | grep -q "Python 3.0" \
        && $SED -i -e "/assert_builtin.open./d" protect_code.pt
}
