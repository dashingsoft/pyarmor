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

# Set the output path of final bundle
OUTPUT=dist

# Options pass to run PyInstaller, for example
# EX_OPTIONS=--onefile --hidden-import comtypes
EX_OPTIONS=
[[ -n "${EX_OPTIONS}" ]] && EX_OPTIONS="-e ' ${EX_OPTIONS}'"

# Options passed to obfuscate scripts, for example
# XOPTIONS=--exclude test --restrict 0
XOPTIONS=
[[ "${XOPTIONS}" ]] && XOPTIONS="-x ' ${XOPTIONS}'"

OPTIONS=
[[ -n "$OUTPUT" ]] && OPTIONS="$OPTIONS --output $OUTPUT"

$PYARMOR pack ${EX_OPTIONS} $XOPTIONS $OPTIONS "${ENTRY_SCRIPT}"
