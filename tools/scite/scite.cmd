@echo off

call D:\bin\development\compilers\env.cmd tools

set PATH=%PATH%;%WORKPATH%\settings\scite\lua
set PATH=%PATH%;D:\bin\tools\gnu_tools

set USERPROFILE=%WORKPATH%\settings\scite
set HOME=%WORKPATH%\settings\scite

start /b %WORKBIN%\development\editors\wscite\SciTE.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
