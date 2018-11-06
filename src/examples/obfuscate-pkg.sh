#
# Sample script used to obfuscate a python package.
#
# Before run it, all TODO variables need to set correctly.
#

# TODO: python interpreter
PYTHON=python

# TODO: Absolute path of pyarmor installed, where to find pyarmor.py
PYARMOR_PATH=/usr/local/lib/python2.7/dist-packages/pyarmor

# TODO: Absolute path in which all python scripts will be obfuscated
SOURCE=/home/jondy/workspace/project/src

# TODO: Package name, __init__.py shoule be in $SOURCE/$PKGNAME
PKGNAME=foo

# TODO: Output path for obfuscated package and runtime files
OUTPUT=/home/jondy/workspace/project/dist

# TODO: Comment next line if do not try to test obfuscated package
TEST_OBFUSCATED_PACKAGE=1

# TODO: Let obfuscated package expired on some day, uncomment next line
# LICENSE_EXPIRED_DATE=2019-01-01

# Check package
PKGPATH=$SOURCE/$PKGNAME
if ! [[ -d "$SOURCE" ]] ; then
    echo "No $SOURCE found, check variable SOURCE" && exit 1
fi
if ! [[ -d "$PKGPATH" ]] ; then
    echo "No $PKGNAME found, check variable PKGNAME" && exit 1
fi
if ! [[ -f "$PKGPATH/__init__.py" ]] ; then
    echo "No __init__.py found in $PKGPATH, check variable SOURCE and PKGNAME" && exit 1
fi

# Obfuscate scripts
cd ${PYARMOR_PATH}
$PYTHON pyarmor.py obfuscate --recursive --no-restrict --src "$PKGPATH" --entry "__init__.py" --output "${OUTPUT}/$PKGNAME" || exit 1

# Generate an expired license if any
if [[ -n "${LICENSE_EXPIRED_DATE}" ]] ; then
    echo
    LICENSE_CODE="expired-${LICENSE_EXPIRED_DATE}"
    $PYTHON pyarmor.py licenses --disable-restrict-mode --expired ${LICENSE_EXPIRED_DATE} ${LICENSE_CODE} || exit 1
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
