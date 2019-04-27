#
# Sample script used to pack obfuscated scripts with
#
#    PyInstaller, py2exe, py2app, cx_Freeze
#
# Before run it, all TODO variables need to set correctly.
#

# TODO:
PYARMOR=pyarmor

# TODO: Entry script
ENTRY_SCRIPT=/home/jondy/workspace/project/src/main.py

# Default is setup.py, or ENTRY_NAME.spec
SETUP_SCRIPT=

# Default is same as the output path of setup script
OUTPUT=

OPTIONS=
[[ -n "${SETUP_SCRIPT}" ]] && OPTIONS="$OPTIONS --setup ${SETUP_SCRIPT}"
[[ -n "$OUTPUT" ]] && OPTIONS="$OPTIONS --output $OUTPUT"

$PYARMOR pack $OPTIONS "${ENTRY_SCRIPT}"
