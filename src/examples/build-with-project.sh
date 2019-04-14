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

# TODO:
PYARMOR=pyarmor

# TODO: Absolute path in which all python scripts will be obfuscated
SOURCE=/home/jondy/workspace/project/src

# TODO: Entry script filename, must be relative to $SOURCE
#       For package, set to __init__.py
ENTRY_SCRIPT=__init__.py

# TODO: output path for saving project config file, and obfuscated scripts
PROJECT=/home/jondy/workspace/project/pyarmor-dist

# TODO: Filter the source files
# PROJECT_FILTER="global-include *.py, prune test"

# TODO: If generate new license for obfuscated scripts, uncomment next line
# LICENSE_CODE=any-identify-string

# Extra information for new license, uncomment the corresponding lines as your demand
# They're useless if LICENSE_CODE is not set

# LICENSE_EXPIRED_DATE="--expired 2019-01-01"
# LICENSE_HARDDISK_SERIAL_NUMBER="--bind-disk SF210283KN"
# LICENSE_MAC_ADDR="--bind-mac 70:38:2a:4d:6f"
# LICENSE_IPV4_ADDR="--bind-ipv4 192.168.121.101"

# TODO: Comment next line if do not try to test obfuscated project
TEST_OBFUSCATED_PROJECT=1

# Set PKGNAME if it's a package
PKGNAME=
if [[ "${ENTRY_SCRIPT}" == "__init__.py" ]] ; then
    PKGNAME=$(basename $SOURCE)
    echo -e "\nPackage name is $PKGNAME\n"
fi

# Create a project
$PYARMOR init --src=$SOURCE --entry=${ENTRY_SCRIPT} $PROJECT || exit 1

# Change to project path
cd $PROJECT

# Filter source files by config project filter
if [[ -n "${PROJECT_FILTER}" ]] ; then
  $PYARMOR config --manifest "${PROJECT_FILTER}" || exit 1
fi


# Obfuscate scripts by command build
$PYARMOR build || exit 1

# Generate special license if any
if [[ -n "${LICENSE_CODE}" ]] ; then
    echo
    $PYARMOR licenses ${LICENSE_EXPIRED_DATE} ${LICENSE_HARDDISK_SERIAL_NUMBER} \
        ${LICENSE_MAC_ADDR} ${LICENSE_IPV4_ADDR} ${LICENSE_CODE} || exit 1
    echo

    # Overwrite default license with this license
    if [[ -n "${PKGNAME}" ]] ; then
        echo Copy new license to $PROJECT/dist
        cp licenses/${LICENSE_CODE}/license.lic $PROJECT/dist/${PKGNAME}
    else
        echo Copy new license to $PROJECT/dist/${PKGNAME}
        cp licenses/${LICENSE_CODE}/license.lic $PROJECT/dist
    fi
fi

# Run obfuscated scripts if
if [[ "${TEST_OBFUSCATED_PROJECT}" == "1"  && -n "${ENTRY_SCRIPT}" ]] ; then

    # Test package
    if [[ -n "${PKGNAME}" ]] ; then
        echo
        echo Prepare to import obfuscated package, run
        echo   python -c "import $PKGNAME"

        cd $PROJECT/dist
        $PYTHON -c "import ${PKGNAME}" && echo -e "\nImport obfuscated package $PKGNAME successfully.\n"
        echo

        # Test script
    else
        echo
        cd $PROJECT/dist
        $PYTHON ${ENTRY_SCRIPT}
        echo
    fi

fi
