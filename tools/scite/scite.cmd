@echo off

set PATH=%PATH%;%~dp0
rem set PATH=%PATH%;C:\bin\ctags
rem set PATH=%PATH%;C:\bin\astyle\bin
rem set PATH=%PATH%;C:\bin\putty
set PATH=%PATH%;C:\Python32

set USERPROFILE=%~dp0
set HOME=%~dp0

start /b C:\bin\wscite\SciTE.exe %1
rem %2 %3 %4 %5 %6 %7 %8 %9
