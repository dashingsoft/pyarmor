@ECHO OFF
REM
REM Sample script used to obfuscate a python package.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO:
SET PYTHON=C:\Python37\python.exe

REM TODO:
SET PYARMOR=C:\Python37\Scripts\pyarmor.exe

REM TODO: Package path
SET PKGPATH=C:\Python37\Lib\site-packages\pyarmor\examples\testpkg

REM TODO: Package name, __init__.py shoule be in %PKGPATH%\%PKGNAME%
SET PKGNAME=mypkg
SET ENTRY_SCRIPT=%PKGPATH%\%PKGNAME%\__init__.py

REM TODO: Output path for obfuscated package and runtime files
SET OUTPUT=C:\Python37\Lib\site-packages\pyarmor\examples\dist

REM TODO: Comment next line if do not try to test obfuscated package
SET TEST_OBFUSCATED_PACKAGE=1

REM TODO: Let obfuscated package expired on some day, uncomment next line
rem SET LICENSE_EXPIRED_DATE=2020-10-01

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

REM Generate an expired license if LICENSE_EXPIRED_DATE is set
SET LICENSE_CODE=r002
SET WITH_LICENSE=
IF DEFINED LICENSE_EXPIRED_DATE (
  %PYARMOR% licenses --expired %LICENSE_EXPIRED_DATE% %LICENSE_CODE%
  IF NOT ERRORLEVEL 0 GOTO END

  REM Specify license file by option --with-license
  SET WITH_LICENSE=--with-license licenses\%LICENSE_CODE%\license.lic
)

REM Obfuscate all .py files in the package
ECHO.
%PYARMOR% obfuscate --recursive --output %OUTPUT%\%PKGNAME% %WITH_LICENSE% %ENTRY_SCRIPT%
IF NOT ERRORLEVEL 0 GOTO END
ECHO.

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
