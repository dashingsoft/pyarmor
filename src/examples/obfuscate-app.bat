@ECHO OFF
REM
REM Sample script used to obfuscate python scripts.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO:
SET PYTHON=C:\Python34\python.exe

REM TODO: Where to find pyarmor.py
SET PYARMOR_PATH=C:\Python34\Lib\site-packages\pyarmor

REM TODO: Absolute path in which all python scripts will be obfuscated
SET SOURCE=%PYARMOR_PATH%\examples\simple

REM TODO: Entry script filename, must be relative to %SOURCE%
SET ENTRY_SCRIPT=queens.py

REM TODO: Output path for obfuscated scripts and runtime files
SET OUTPUT=%PYARMOR_PATH%\examples\dist

REM TODO: Let obfuscated scripts expired on some day, uncomment next line
rem SET LICENSE_EXPIRED_DATE=2019-01-01

REM TODO: If try to run obfuscated scripts, uncomment next line
rem SET TEST_OBFUSCATED_SCRIPTS=1

REM Check Python
%PYTHON% --version
IF NOT ERRORLEVEL 0 (
  ECHO.
  ECHO Python doesn't work, check value of variable PYTHON
  ECHO.
  GOTO END
)

REM Check Pyarmor
IF NOT EXIST "%PYARMOR_PATH%\pyarmor.py" (
  ECHO.
  ECHO No pyarmor found, check value of variable PYARMOR_PATH
  ECHO.
  GOTO END
)

REM Check Source
IF NOT EXIST "%SOURCE%" (
  ECHO.
  ECHO No %SOURCE% found, check value of variable SOURCE
  ECHO.
  GOTO END
)

REM Obfuscate all the ".py" files
ECHO.
CD /D %PYARMOR_PATH%
%PYTHON% pyarmor.py obfuscate --recursive --src %SOURCE% --entry %ENTRY_SCRIPT% --output %OUTPUT%
IF NOT ERRORLEVEL 0 GOTO END
ECHO.

REM Generate an expired license if LICENSE_EXPIRED_DATE is set
SET LICENSE_CODE=expired-%LICENSE_EXPIRED_DATE%
IF DEFINED LICENSE_EXPIRED_DATE (
  %PYTHON% pyarmor.py licenses --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
  IF ERRORLEVEL 1 GOTO END

  REM Overwrite default license with this expired license
  ECHO.
  ECHO Copy expired license to %OUTPUT%
  COPY licenses\%LICENSE_CODE%\license.lic %OUTPUT%
  ECHO.
)

REM Test obfuscated scripts
IF "%TEST_OBFUSCATED_SCRIPTS%" == "1" (
  ECHO Prepare to run obfuscated script %OUTPUT%\%ENTRY_SCRIPT%
  PAUSE

  CD /D %OUTPUT%
  %PYTHON% %ENTRY_SCRIPT%
)

:END

ENDLOCAL
PAUSE
