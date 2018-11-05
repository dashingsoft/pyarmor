@ECHO OFF
REM
REM Sample script used to obfuscate python scripts.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO: Absolute path for python installed, python.exe should be here
SET PYPATH=C:\Users\User\AppData\Local\Programs\Python\Python36-32

REM TODO: Absolute path in which all python scripts will be obfuscated
SET SOURCE=D:\My Workspace\Project\Src

REM TODO: Entry script filename, must be relative to %SOURCE%
SET ENTRY_SCRIPT=main.py

REM TODO: Output path for obfuscated scripts and runtime files
SET OUTPUT=D:\My Workspace\Project\Dist

REM TODO: Let obfuscated scripts expired on some day, uncomment next line
Rem SET LICENSE_EXPIRED_DATE=2019-01-01

REM TODO: If try to run obfuscated scripts, uncomment next line
Rem SET TEST_OBFUSCATED_SCRIPTS=1

REM Check Python
SET PYTHON=%PYPATH%\python.exe
IF NOT EXIST "%PYTHON%" (
  ECHO
  ECHO No python.exe found in %PYPATH%
  ECHO
  GOTO END
)

REM Check Pyarmor
SET PYARMOR_PATH=%PYPATH%\Lib\site-packages\pyarmor
IF NOT EXIST "%PYARMOR_PATH%\pyarmor.py" (
  ECHO
  ECHO No pyarmor installed, run "pip install pyarmor" to install it first
  ECHO If pyarmor has been installed other than pip, set variable PYARMOR_PATH to the right path
  ECHO 
  GOTO END
)

REM Obfuscate scripts
CD /D %PYARMOR_PATH%
%PYTHON% pyarmor.py obfuscate --recursive --src %SOURCE% --entry %ENTRY_SCRIPT% --output %OUTPUT%

REM Somehing is wrong
IF ERRORLEVEL 1 GOTO END

REM Generate an expired license if any
IF DEFINED LICENSE_EXPIRED_DATE (
  SET LICENSE_CODE=expired-%LICENSE_EXPIRED_DATE%
  %PYTHON% pyarmor.py licenses --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
  IF ERRORLEVEL 1 GOTO END
  
  REM Overwrite default license with this expired license
  ECHO The obfuscated scripts will be expired on %LICENSE_EXPIRED_DATE%
  COPY licenses\%LICENSE_CODE%\license.lic %OUTPUT%
)

REM Run obfuscated scripts
IF "%TEST_OBFUSCATED_SCRIPTS%" == "1" (
  SETLOCAL
  CD /D %OUTPUT%
  %PYTHON% %ENTRY_SCRIPT%
  ENDLOCAL
)

:END

ENDLOCAL
PAUSE
