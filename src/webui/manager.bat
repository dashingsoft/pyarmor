@ECHO OFF

SETLOCAL

FOR /D %%I IN (C:\Python*) DO SET PYPATH=%%I

IF "%PYPATH%" == "" (

  ECHO No python found in C:\PythonXY.
  PAUSE

) ELSE (

  ECHO Change current path to %~dp0
  CD /D %~dp0

  ECHO Use %PYPATH% to run server ...
  %PYPATH%\python.exe server.py

  IF ERRORLEVEL 1 PAUSE

)

ENDLOCAL