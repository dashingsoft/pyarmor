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

# TODO: Let obfuscated package expired on some day, uncomment next line
#LICENSE_EXPIRED_DATE=2019-01-01

# TODO: If try to test obfuscated package, uncomment next line
#TEST_OBFUSCATED_PACKAGE=1

# Check package
PKGPATH=$SOURCE/$PKGNAME
[[ -f "$PKGPATH/__init__.py" ]] || ( echo "No __init__.py found in package path $PKGPATH" && exit 1 )


# Obfuscate scripts
cd ${PYARMOR_PATH}
$PYTHON pyarmor.py obfuscate --recursive --no-restrict --src "$PKGPATH" --entry "__init__.py" --output "${OUTPUT}/$PKGNAME" || exit 1

# Generate an expired license if any
if ! [[ "${LICENSE_EXPIRED_DATE}" == "" ]] ; then
  RCODE="expired-${LICENSE_EXPIRED_DATE}"
  $PYTHON pyarmor.py licenses --expired ${LICENSE_EXPIRED_DATE} $RCODE || exit 1

  # Overwrite default license with this expired license
  echo "The obfuscated scripts will be expired on ${LICENSE_EXPIRED_DATE}"
  cp licenses/$RCODE/license.lic ${OUTPUT}/$PKGNAME
)

# Run obfuscated scripts if
if [[ "${TEST_OBFUSCATED_PACKAGE}" == "1" ]] ; then
  cd ${OUTPUT}
  $PYTHON -c "import $PKGNAME"
fi
