@ECHO OFF
REM
REM Sample script used to pack obfuscated scripts with
REM
REM    PyInstaller, py2exe, py2app, cx_Freeze
REM
REM Before run it, all TODO variables need to set correctly.
REM

SetLocal

REM TODO:
Set PYARMOR=C:\Python34\Scripts\pyarmor.exe

REM TODO: Entry script
Set ENTRY_SCRIPT=C:\Python34\Lib\site-packages\pyarmor\examples\py2exe\hello.py

REM Default is setup.py, or ENTRY_NAME.spec
Set SETUP_SCRIPT=

REM Default is same as the output path of setup script
OUTPUT=

Set OPTIONS=
If NOT "%SETUP_SCRIPT%" == "" %OPTIONS%=%OPTIONS% --setup %SETUP_SCRIPT%
If NOT "%OUTPUT%" == "" %OPTIONS%=%OPTIONS% --output %OUTPUT%

%PYARMOR% %OPTIONS% %ENTRY_SCRIPT%

EndLocal

Pause