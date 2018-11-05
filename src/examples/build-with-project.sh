#
# Sample script used to obfuscate python source files with prroject
#
# There are several advantages to manage obfuscated scripts by project:
#
#   Increment build, only updated scripts are obfuscated since last build
#   Filter scripts, for example, exclude all the test scripts
#   More convenient command to manage obfuscated scripts
#

# TODO: python interpreter
PYTHON=python

# TODO: Absolute path of pyarmor installed, where to find pyarmor.py
PYARMOR_PATH=/usr/local/lib/

# TODO: Absolute path in which all python scripts will be obfuscated
SOURCE=/home/jondy/workspace/project/src

# TODO: Entry script filename, must be relative to $SOURCE
#       For package, set to __init__.py
ENTRY_SCRIPT=__init__.py

# TODO: output path for saving project config file, and obfuscated scripts
PROJECT=/home/jondy/workspace/project/pyarmor-dist

# TODO: Filter the source files
#PROJECT_FILTER="global-include *.py, prune: test"

# TODO: If generate special license for obfuscated scripts, uncomment next line
#LICENSE_CODE=special-user

# Extra information for special license, uncomment the corresponding lines as your demand
# They're useness if LICENSE_CODE is not set

#LICENSE_EXPIRED_DATE=2019-01-01
#LICENSE_HARDDISK_SERIAL_NUMBER=SF210283KN
#LICENSE_MAC_ADDR=70:38:2a:4d:6f
#LICENSE_IPV4_ADDR=192.168.121.101

# TODO: If try to test obfuscated files, uncomment next line
#TEST_OBFUSCATED_FILES=1

# Set PACKAGE_NAME if it's a package
if [[ "${ENTRY_SCRIPT}" == "__init__.py" ]] ; then
    PACKAGE_NAME=$(basename $SOURCE)
fi

# Create a project
cd ${PYARMOR_PATH}
$PYTHON pyarmor.py init --src=$SOURCE --entry=${ENTRY_SCRIPT} $PROJECT

# Change to project path, there is a convenient script pyarmor.bat
cd $PROJECT

# Filter source files by config project filter
if [[ -n "${PROJECT_FILTER}" ]] ; then
  ./pyarmor.sh config --manifest "${PROJECT_FILTER}" || exit 1
fi


# Obfuscate scripts by command build
./pyarmor.sh build || exit 1

# Generate special license if any
if [[ -n "${LICENSE_CODE}" ]] ; then
  LICENSE_OPTIONS=""
  [[ -n "${LICENSE_EXPIRED_DATE SET}" ]] && LICENSE_OPTIONS="${LICENSE_OPTIONS} --expired %LICENSE_EXPIRED_DATE%"
  [[ -n "${LICENSE_HARDDISK_SERIAL_NUMBER}" ]] && LICENSE_OPTIONS="${LICENSE_OPTIONS} --bind-disk ${LICENSE_HARDDISK_SERIAL_NUMBER}"
  [[ -n "${LICENSE_MAC_ADDR}" ]] && LICENSE_OPTIONS="${LICENSE_OPTIONS} --bind-mac ${LICENSE_MAC_ADDR}"
  [[ -n "${LICENSE_IPV4_ADDR}" ]] && LICENSE_OPTIONS="${LICENSE_OPTIONS} --bind-ipv4 ${LICENSE_IPV4_ADDR}"

  ./pyarmor.sh licenses ${LICENSE_OPTIONS} ${LICENSE_CODE} || exit 1

  # Overwrite default license with this license
  echo Replace default license with "licenses/${LICENSE_CODE}/license.lic"
  if [[ -n "${PACKAGE_NAME}" ]] ; then
    cp licenses/${LICENSE_CODE}/license.lic $PROJECT/dist
  else
    cp licenses/${LICENSE_CODE}/license.lic $PROJECT/dist/${PACKAGE_NAME}
  fi
fi

# Run obfuscated scripts if
if [[ "${TEST_OBFUSCATED_FILES}" == "1"  && -n "${ENTRY_SCRIPT}" ]] ; then

  # Test package
  if [[ -n "${PACKAGE_NAME}" ]] ; then
    cd $PROJECT/dist
    $PYTHON -c "import ${PACKAGE_NAME}"

  # Test script
  else
    cd $PROJECT/dist
    $PYTHON ${ENTRY_SCRIPT}
  fi

fi
