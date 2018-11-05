@ECHO OFF
SETLOCAL

REM TODO: Fullpath for python installed
SET PYPATH=C:\Users\User\AppData\Local\Programs\Python\Python36-32

REM TODO: Fullpath in which all python scripts will be obfuscated
SET SOURCE=D:\My Workspace\Project\Src

REM TODO: Entry script filename, must be relative to %SOURCE%
SET ENTRY_SCRIPT=main.py

REM TODO: Output path for obfuscated scripts and runtime files
SET OUTPUT=D:\My Workspace\Project\Dist

REM TODO: Let obfuscated scripts expired on some day, uncomment next line
REM SET PYARMOR_EXPIRED_DATE=2019-01-01

REM TODO: If want to run obfuscated scripts, uncomment next line
REM TEST_OBFUSCATED_SCRIPTS=1

REM Check environments
SET PYTHON=%PYPATH%\python.exe
SET PYARMOR_PATH=%PYPATH%\Lib\site-packages\pyarmor

IF NOT EXIST "%PYTHON%" (
  ECHO No python.exe found in %PYPATH%
  GOTO END
)

IF NOT EXIST "%PYARMOR_PATH%\pyarmor.py" (
  ECHO No pyarmor installed, run "pip install pyarmor" to install it first
  GOTO END
)

REM Obfuscate scripts
CD /D %PYARMOR_PATH%
%PYTHON% pyarmor.py obfuscate --recursive --src %SOURCE% --entry %ENTRY_SCRIPT% --output %OUTPUT%

REM Somehing is wrong
IF ERRORLEVEL 1 GOTO END

REM Generate an expired license if any
IF DEFINED EXPIRED_DATE (
  SET RCODE=expired-%PYARMOR_EXPIRED_DATE%
  %PYTHON% pyarmor.py obfuscate licenses --expired %PYARMOR_EXPIRED_DATE% %RCODE%
  IF ERRORLEVEL 1 GOTO END
  
  REM Overwrite default license with this expired license
  ECHO The obfuscated scripts will be expired on %PYARMOR_EXPIRED_DATE%
  COPY licenses\%RCODE%\license.lic %OUTPUT%
)

REM Run obfuscated scripts if 
IF "TEST_OBFUSCATED_SCRIPTS" == "1" (
  SETLOCAL
  CD /D %OUTPUT%
  %PYTHON% %ENTRY_SCRIPT%
  ENDLOCAL
)

:END

ENDLOCAL
PAUSE
