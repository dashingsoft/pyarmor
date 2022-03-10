@ECHO OFF
REM
REM Sample script used to obfuscate python scripts.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO:
SET PYTHON=C:\Python37\python.exe

REM TODO:
SET PYARMOR=C:\Python37\Scripts\pyarmor.exe

REM TODO: Entry script filename
SET ENTRY_SCRIPT=C:\Python37\Lib\site-packages\pyarmor\examples\simple\queens.py

REM TODO: Output path for obfuscated scripts and runtime files
SET OUTPUT=C:\Python37\Lib\site-packages\pyarmor\examples\simple\dist

REM TODO: Let obfuscated scripts expired on some day, uncomment next line
SET LICENSE_EXPIRED_DATE=2020-10-01

REM TODO: If try to run obfuscated scripts, uncomment next line
SET TEST_OBFUSCATED_SCRIPTS=1

REM Check entry script
IF NOT EXIST "%ENTRY_SCRIPT%" (
  ECHO.
  ECHO No %ENTRY_SCRIPT% found, check value of variable ENTRY_SCRIPT
  ECHO.
  GOTO END
)

REM Generate an expired license if LICENSE_EXPIRED_DATE is set
SET LICENSE_CODE=r001
SET WITH_LICENSE=
IF DEFINED LICENSE_EXPIRED_DATE (
  %PYARMOR% licenses --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
  IF ERRORLEVEL 1 GOTO END

  REM Specify license file by option --with-license
  SET WITH_LICENSE=--with-license licenses\%LICENSE_CODE%\license.lic
)

REM Obfuscate all the ".py" files
ECHO.
%PYARMOR% obfuscate --recursive --output %OUTPUT% %WITH_LICENSE% %ENTRY_SCRIPT%
IF NOT ERRORLEVEL 0 GOTO END
ECHO.

REM Test obfuscated scripts
IF "%TEST_OBFUSCATED_SCRIPTS%" == "1" (
  ECHO Prepare to run obfuscated script
  PAUSE

  CD /D %OUTPUT%
  FOR %%I IN ( %ENTRY_SCRIPT% ) DO %PYTHON% %%~nI.py
)

:END

ENDLOCAL
PAUSE
