#
# Sample script used to obfuscate python scripts.
#
# Before run it, all TODO variables need to set correctly.
#

# TODO: python interpreter
PYTHON=python

# TODO: Absolute path of pyarmor installed, where to find pyarmor.py
PYARMOR_PATH=/usr/local/lib/python2.7/dist-packages/pyarmor

# TODO: Absolute path in which all python scripts will be obfuscated
SOURCE=/home/jondy/workspace/project/src

# TODO: Entry script filename, must be relative to $SOURCE
ENTRY_SCRIPT=main.py

# TODO: Output path for obfuscated scripts and runtime files
OUTPUT=/home/jondy/workspace/project/dist

# TODO: Let obfuscated scripts expired on some day, uncomment next line
# LICENSE_EXPIRED_DATE=2019-01-01

# TODO: If try to run obfuscated scripts, uncomment next line
# TEST_OBFUSCATED_SCRIPTS=1

# Obfuscate scripts
cd ${PYARMOR_PATH}
$PYTHON pyarmor.py obfuscate --recursive --src "$SOURCE" --entry "${ENTRY_SCRIPT}" --output $OUTPUT || exit 1

# Generate an expired license if any
if [[ -n "${LICENSE_EXPIRED_DATE}" ]] ; then
    echo
    LICENSE_CODE="expired-${LICENSE_EXPIRED_DATE}"
    $PYTHON pyarmor.py licenses --expired ${LICENSE_EXPIRED_DATE} ${LICENSE_CODE} || exit 1
    echo

    # Overwrite default license with this expired license
    echo Copy expired license to $OUTPUT
    cp  licenses/${LICENSE_CODE}/license.lic $OUTPUT
fi

# Run obfuscated scripts
if [[ "${TEST_OBFUSCATED_SCRIPTS}" == "1" ]] ; then
    echo
    cd $OUTPUT
    $PYTHON ${ENTRY_SCRIPT}
    echo
fi
