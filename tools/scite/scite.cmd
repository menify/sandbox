@echo off

rem call D:\bin\development\compilers\env.cmd tools

set PATH=%PATH%;%~dp0
set PATH=%PATH%;C:\bin\ctags
set PATH=%PATH%;C:\bin\astyle\bin
set PATH=%PATH%;C:\bin\putty
set PATH=%PATH%;C:\Python27

set USERPROFILE=%~dp0
set HOME=%~dp0

start /b C:\bin\wscite\SciTE.exe %1
rem %2 %3 %4 %5 %6 %7 %8 %9
