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
# LICENSE_EXPIRED_DATE=2019-01-01

# Check package
if ! [[ -d "$PKGPATH" ]] ; then
    echo "No $PKGPATH found, check variable PKGPATH" && exit 1
fi
if ! [[ -d "${ENTRY_SCRIPT}" ]] ; then
    echo "No ${ENTRY_SCRIPT} found, check variable PKGPATH and PKGNAME" && exit 1
fi

# Obfuscate scripts
$PYARMOR obfuscate --recursive --output "${OUTPUT}/$PKGNAME" "${ENTRY_SCRIPT}"  || exit 1

# Generate an expired license if any
if [[ -n "${LICENSE_EXPIRED_DATE}" ]] ; then
    echo
    LICENSE_CODE="expired-${LICENSE_EXPIRED_DATE}"
    $PYARMOR licenses --expired ${LICENSE_EXPIRED_DATE} ${LICENSE_CODE} || exit 1
    echo

    # Overwrite default license with this expired license
    echo "Copy expired license to ${OUTPUT}/$PKGNAME"
    cp licenses/${LICENSE_CODE}/license.lic ${OUTPUT}/$PKGNAME
fi

# Run obfuscated scripts if
if [[ "${TEST_OBFUSCATED_PACKAGE}" == "1" ]] ; then
    echo
    echo Prepare to import obfuscated package, run
    echo   python -c "import $PKGNAME"

    cd ${OUTPUT}
    $PYTHON -c "import $PKGNAME" && echo -e "\nImport obfuscated package $PKGNAME successfully.\n"
    echo
fi
