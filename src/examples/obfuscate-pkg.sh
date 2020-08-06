#
# Sample script used to obfuscate a python package.
#
# Before run it, all TODO variables need to set correctly.
#

# TODO:
PYTHON=python

# TODO:
PYARMOR=pyarmor

# TODO: Package path
PKGPATH=/home/jondy/workspace/project/src

# TODO: Package name, __init__.py shoule be in $PKGPATH/$PKGNAME
PKGNAME=foo
ENTRY_SCRIPT=$PKGPATH/$PKGNAME/__init__.py

# TODO: Output path for obfuscated package and runtime files
OUTPUT=/home/jondy/workspace/project/dist

# TODO: Comment next line if do not try to test obfuscated package
TEST_OBFUSCATED_PACKAGE=1

# TODO: Let obfuscated package expired on some day, uncomment next line
# LICENSE_EXPIRED_DATE=2020-10-01

# Check package
if ! [[ -d "$PKGPATH" ]] ; then
    echo "No $PKGPATH found, check variable PKGPATH" && exit 1
fi
if ! [[ -d "${ENTRY_SCRIPT}" ]] ; then
    echo "No ${ENTRY_SCRIPT} found, check variable PKGPATH and PKGNAME" && exit 1
fi

# Generate an expired license if any
if [[ -n "${LICENSE_EXPIRED_DATE}" ]] ; then
    echo
    LICENSE_CODE="r002"
    $PYARMOR licenses --expired ${LICENSE_EXPIRED_DATE} ${LICENSE_CODE} || exit 1
    echo

    # Specify license file by option --with-license
    WITH_LICENSE="--with-license licenses/${LICENSE_CODE}/license.lic"
fi

# Obfuscate all .py files in the package
$PYARMOR obfuscate --recursive --output "${OUTPUT}/$PKGNAME" ${WITH_LICENSE} "${ENTRY_SCRIPT}"  || exit 1

# Run obfuscated scripts if
if [[ "${TEST_OBFUSCATED_PACKAGE}" == "1" ]] ; then
    echo
    echo Prepare to import obfuscated package, run
    echo   python -c "import $PKGNAME"

    cd ${OUTPUT}
    $PYTHON -c "import $PKGNAME" && echo -e "\nImport obfuscated package $PKGNAME successfully.\n"
    echo
fi
