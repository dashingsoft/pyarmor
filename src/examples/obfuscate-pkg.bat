@ECHO OFF
REM
REM Sample script used to obfuscate a python package.
REM
REM Before run it, all TODO variables need to set correctly.
REM

SETLOCAL

REM TODO: Absolute path for python installed, python.exe should be here
SET PYPATH=C:\Users\User\AppData\Local\Programs\Python\Python36-32

REM TODO: Absolute parent path of package
SET SOURCE=D:\My Workspace\Project\Src

REM TODO: Package name, __init__.py shoule be in %SOURCE%\%PKGNAME%
SET PKGNAME=foo

REM TODO: Output path for obfuscated package and runtime files
SET OUTPUT=D:\My Workspace\Project\Dist

REM TODO: Let obfuscated package expired on some day, uncomment next line
Rem SET LICENSE_EXPIRED_DATE=2019-01-01

REM TODO: If try to test obfuscated package, uncomment next line
Rem SET TEST_OBFUSCATED_PACKAGE=1

REM Check package
SET PKGPATH=%SOURCE%\%PKGNAME%
IF NOT EXIST "%PKGPATH%\__init__.py" (
  ECHO
  ECHO No __init__.py found in package path %PKGPATH%
  ECHO
  GOTO END
)

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
%PYTHON% pyarmor.py obfuscate --recursive --src %PKGPATH% --entry __init__.py --output %OUTPUT%\%PKGNAME%

REM Somehing is wrong
IF ERRORLEVEL 1 GOTO END

REM Generate an expired license if any
IF DEFINED LICENSE_EXPIRED_DATE (
  SET RCODE=expired-%LICENSE_EXPIRED_DATE%
  %PYTHON% pyarmor.py licenses --expired %LICENSE_EXPIRED_DATE% %RCODE%
  IF ERRORLEVEL 1 GOTO END
  
  REM Overwrite default license with this expired license
  ECHO The obfuscated scripts will be expired on %LICENSE_EXPIRED_DATE%
  COPY licenses\%RCODE%\license.lic %OUTPUT%\%PKGNAME%
)

REM Run obfuscated scripts if 
IF "%TEST_OBFUSCATED_PACKAGE%" == "1" (
  SETLOCAL
  CD /D %OUTPUT%
  %PYTHON% -c 'import %PKGNAME%'
  ENDLOCAL
)

:END

ENDLOCAL
PAUSE
