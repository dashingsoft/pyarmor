@ECHO OFF
REM
REM Sample script used to obfuscate python source files with prroject
REM
REM There are several advantages to manage obfuscated scripts by project:
REM
REM   * Increment build, only updated scripts are obfuscated since last build
REM   * Filter scripts, for example, exclude all the test scripts
REM   * More convenient command to manage obfuscated scripts
REM

SETLOCAL

REM TODO: Absolute path for python installed, python.exe should be here
SET PYPATH=C:\Users\User\AppData\Local\Programs\Python\Python36-32

REM TODO: Absolute path in which all python scripts will be obfuscated
SET SOURCE=D:\My Workspace\Project\Src

REM TODO: Entry script filename, must be relative to %SOURCE%
REM       For package, set to __init__.py
SET ENTRY_SCRIPT=__init__.py

REM TODO: output path for saving project config file, and obfuscated scripts
SET PROJECT=D:\My Workspace\Project\Pyarmor-Dist

REM TODO: Filter the source files
Rem SET PROJECT_FILTER=global-include *.py, prune: test

REM TODO: If generate special license for obfuscated scripts, uncomment next line
Rem SET LICENSE_CODE=special-user

REM Extra information for special license, uncomment the corresponding lines as your demand
REM They're useness if LICENSE_CODE is not set

Rem SET LICENSE_EXPIRED_DATE=2019-01-01
Rem SET LICENSE_HARDDISK_SERIAL_NUMBER=SF210283KN
Rem SET LICENSE_MAC_ADDR=70:38:2a:4d:6f
Rem SET LICENSE_IPV4_ADDR=192.168.121.101

REM TODO: If try to test obfuscated files, uncomment next line
Rem SET TEST_OBFUSCATED_FILES=1

REM Set PACKAGE_NAME if it's a package
IF "%ENTRY_SCRIPT%" == "__init__.py" (
  FOR %%i in ( %SOURCE% ) do SET PACKAGE_NAME=%%~ni%
) ELSE (
  SET PACKAGE_NAME=
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

REM Create a project
CD /D %PYARMOR_PATH%
%PYTHON% pyarmor.py init --src=%SOURCE% --entry=%ENTRY_SCRIPT% %PROJECT%

REM Change to project path, there is a convenient script pyarmor.bat
cd /D %PROJECT%

REM Filter source files by config project filter
IF DEFINED PROJECT_FILTER (
  .\pyarmor.bat config --manifest "%PROJECT_FILTER%"
  IF ERRORLEVEL 1 GOTO END
)

REM Obfuscate scripts by command build
.\pyarmor.bat build

IF ERRORLEVEL 1 GOTO END

REM Generate special license if any
IF DEFINED LICENSE_CODE (

  SET LICENSE_OPTIONS=
  IF DEFINE LICENSE_EXPIRED_DATE SET LICENSE_OPTIONS=%LICENSE_OPTIONS% --expired %LICENSE_EXPIRED_DATE%
  IF DEFINE LICENSE_HARDDISK_SERIAL_NUMBER SET LICENSE_OPTIONS=%LICENSE_OPTIONS% --bind-disk %LICENSE_HARDDISK_SERIAL_NUMBER%
  IF DEFINE LICENSE_MAC_ADDR SET LICENSE_OPTIONS=%LICENSE_OPTIONS% --bind-mac %LICENSE_MAC_ADDR%
  IF DEFINE LICENSE_IPV4_ADDR SET LICENSE_OPTIONS=%LICENSE_OPTIONS% --bind-ipv4 %LICENSE_IPV4_ADDR%
  
  .\pyarmor.bat licenses %LICENSE_OPTIONS% %LICENSE_CODE%
  IF ERRORLEVEL 1 GOTO END
  
  REM Overwrite default license with this license
  ECHO Replace default license with "licenses\%LICENSE_CODE%\license.lic"
  IF DEFINED PACKAGE_NAME (
    COPY licenses\%LICENSE_CODE%\license.lic %PROJECT%\dist
  ) ELSE (
    COPY licenses\%LICENSE_CODE%\license.lic %PROJECT%\dist\%PACKAGE_NAME%
  )

)

REM Run obfuscated scripts if 
IF "%TEST_OBFUSCATED_FILES%" == "1"  IF DEFINED ENTRY_SCRIPT (
  SETLOCAL
  
  REM Test package
  IF DEFINED PACKAGE_NAME (
    CD /D %PROJECT%\dist
    %PYTHON% -c "import %PACKAGE_NAME%"
  ) 
  
  REM Test script
  ELSE (
    CD /D %PROJECT%\dist
    %PYTHON% %ENTRY_SCRIPT%
  )
  
  ENDLOCAL
)

:END

ENDLOCAL
PAUSE

