@ECHO OFF
REM
REM Sample script used to obfuscate a python package.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO:
SET PYTHON=C:\Python34\python.exe

REM TODO: Where to find pyarmor.py
SET PYARMOR_PATH=C:\Python34\Lib\site-packages\pyarmor

REM TODO: Absolute path in which all python scripts will be obfuscated
SET SOURCE=%PYARMOR_PATH%\examples\testpkg

REM TODO: Package name, __init__.py shoule be in %SOURCE%\%PKGNAME%
SET PKGNAME=mypkg

REM TODO: Output path for obfuscated package and runtime files
SET OUTPUT=%PYARMOR_PATH%\examples\pkg-dist

REM TODO: Comment next line if do not try to test obfuscated package
SET TEST_OBFUSCATED_PACKAGE=1

REM TODO: Let obfuscated package expired on some day, uncomment next line
SET LICENSE_EXPIRED_DATE=2019-01-01

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

REM Check package
SET PKGPATH=%SOURCE%\%PKGNAME%
IF NOT EXIST "%PKGPATH%\__init__.py" (
  ECHO.
  ECHO No %PKGPATH%\__init__.py found, check value of variable PKGNAME
  ECHO.
  GOTO END
)

REM Obfuscate scripts
ECHO.
CD /D %PYARMOR_PATH%
%PYTHON% pyarmor.py obfuscate --recursive --no-restrict --src %PKGPATH% --entry __init__.py --output %OUTPUT%\%PKGNAME%
IF NOT ERRORLEVEL 0 GOTO END
ECHO.

REM Generate an expired license if LICENSE_EXPIRED_DATE is set
SET LICENSE_CODE=expired-%LICENSE_EXPIRED_DATE%
IF DEFINED LICENSE_EXPIRED_DATE (
  %PYTHON% pyarmor.py licenses --disable-restrict-mode --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
  IF NOT ERRORLEVEL 0 GOTO END

  REM Overwrite default license with this expired license
  ECHO.
  ECHO Copy expired license to %OUTPUT%\%PKGNAME%
  COPY licenses\%LICENSE_CODE%\license.lic %OUTPUT%\%PKGNAME%
  ECHO.
)

REM Try to import obfuscated package if
IF "%TEST_OBFUSCATED_PACKAGE%" == "1" (
  ECHO Prepare to import obfuscated package, run
  ECHO   python -c "import %PKGNAME%"
  ECHO.
  PAUSE

  CD /D %OUTPUT%
  %PYTHON% -c "import %PKGNAME%"
  ECHO.
  ECHO Import obfuscated package %PKGNAME% finished.
  ECHO.
)

:END

ENDLOCAL
PAUSE
