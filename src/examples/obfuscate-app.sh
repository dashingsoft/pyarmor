#
# Sample script used to obfuscate python scripts.
#
# Before run it, all TODO variables need to set correctly.
#

# TODO: python interpreter
PYTHON=python

# TODO:
PYARMOR=pyarmor

# TODO: Entry script filename
ENTRY_SCRIPT=main.py

# TODO: Output path for obfuscated scripts and runtime files
OUTPUT=dist

# TODO: Let obfuscated scripts expired on some day, uncomment next line
# LICENSE_EXPIRED_DATE=2020-10-01

# TODO: If try to run obfuscated scripts, uncomment next line
# TEST_OBFUSCATED_SCRIPTS=1

# Generate an expired license if any
if [[ -n "${LICENSE_EXPIRED_DATE}" ]] ; then
    echo
    LICENSE_CODE=r001
    $PYARMOR licenses --expired ${LICENSE_EXPIRED_DATE} ${LICENSE_CODE} || exit 1
    echo

    # Specify license file by option --with-license
    WITH_LICENSE="--with-license licenses/${LICENSE_CODE}/license.lic"
fi

# Obfuscate scripts
$PYARMOR obfuscate --recursive --output $OUTPUT ${WITH_LICENSE} ${ENTRY_SCRIPT} || exit 1

# Run obfuscated scripts
if [[ "${TEST_OBFUSCATED_SCRIPTS}" == "1" ]] ; then
    echo
    cd $OUTPUT
    $PYTHON $(basename ${ENTRY_SCRIPT})
    echo
fi
