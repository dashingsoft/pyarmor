@ECHO OFF
REM
REM Sample script used to obfuscate a python package.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO:
SET PYTHON=C:\Python34\python.exe

REM TODO:
SET PYARMOR=C:\Python34\Scripts\pyarmor.exe

REM TODO: Package path
SET PKGPATH=C:\Python34\Lib\site-packages\pyarmor\examples\testpkg

REM TODO: Package name, __init__.py shoule be in %PKGPATH%\%PKGNAME%
SET PKGNAME=mypkg
SET ENTRY_SCRIPT=%PKGPATH%\%PKGNAME%\__init__.py 

REM TODO: Output path for obfuscated package and runtime files
SET OUTPUT=C:\Python34\Lib\site-packages\pyarmor\examples\dist

REM TODO: Comment next line if do not try to test obfuscated package
SET TEST_OBFUSCATED_PACKAGE=1

REM TODO: Let obfuscated package expired on some day, uncomment next line
rem SET LICENSE_EXPIRED_DATE=2019-01-01

REM Check Package
IF NOT EXIST "%PKGPATH%" (
  ECHO.
  ECHO No %PKGPATH% found, check value of variable PKGPATH
  ECHO.
  GOTO END
)

REM Check entry script
IF NOT EXIST "%ENTRY_SCRIPT%" (
  ECHO.
  ECHO No %ENTRY_SCRIPT% found, check value of variable PKGNAME
  ECHO.
  GOTO END
)

REM Obfuscate scripts
ECHO.
%PYARMOR% obfuscate --recursive --output %OUTPUT%\%PKGNAME% %ENTRY_SCRIPT%
IF NOT ERRORLEVEL 0 GOTO END
ECHO.

REM Generate an expired license if LICENSE_EXPIRED_DATE is set
SET LICENSE_CODE=expired-%LICENSE_EXPIRED_DATE%
IF DEFINED LICENSE_EXPIRED_DATE (
  %PYARMOR% licenses --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
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
