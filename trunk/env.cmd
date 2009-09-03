@echo off

rem =============================
rem = setting tools environment =
rem =============================

set WORKPATH=D:\work
set WORKBIN=D:\bin
set DEVELOPMENTDIR=%WORKBIN%\development
set COMPILERSDIR=%DEVELOPMENTDIR%\compilers

set PATH=%DEVELOPMENTDIR%\Python25;%DEVELOPMENTDIR%\Python25\Scripts;%PATH%
set PYTHONPATH=%DEVELOPMENTDIR%\Python25\Scripts;%PYTHONPATH%
rem set PYTHONOPTIMIZE=0

set PATH=%PATH%;%DEVELOPMENTDIR%\perl\bin;%DEVELOPMENTDIR%\NaturalDocs

set PATH=%WORKBIN%\tools;%PATH%
REM ~ set PATH=%PATH%;%WORKBIN%\tools\gnu_tools

set PATH=%DEVELOPMENTDIR%\subversion\bin;%PATH%

rem set FLEXLINTDIR=%DEVELOPMENTDIR%\code-analyzers\flexlint
rem set PATH=%FLEXLINTDIR%\bin;%PATH%
rem set LINT=-i%FLEXLINTDIR%\lnt
rem set FLEXLINT_USER_DIR=%WORKPATH%\settings\flexelint
rem set LINT_USER=-i%FLEXLINT_USER_DIR% common.lnt msg_format.lnt

rem set PATH=%PATH%;%WORKBIN%\compilers\nasm

rem set LIB_DIR=%WORKPATH%\src\lib
rem set LIB3PARTY_DIR=%WORKPATH%\src\lib3party

rem set SciTE_HOME=%WORKBIN%\editors\wscite\scite\bin

set SCONSFLAGS=--implicit-cache --max-drift=1
set PYTHONPATH=%WORKPATH%\src\lib;%PYTHONPATH%

rem set QTDIR=%WORKPATH%\src\lib3party\qt-4.2.2
rem set PATH=%QTDIR%\bin;%PATH%

rem set WXWIDGETDIR=%WORKPATH%\src\lib3party\wxwidgets\wxWidgets-2.8.3
rem set WXWIDGET_LIBDIR=%WXWIDGETDIR%\lib\vc_lib
rem set WXWIDGET_INCDIR=%WXWIDGETDIR%\include

echo Environment for tools has been set.
echo.

goto %1

rem ================================
rem = setting compiler environment =
rem ================================

:rvct
echo ARM RVCT environment

set JAVA_HOME=C:\Program Files\Java\jre1.6.0_02
set RVCT22DIR=%COMPILERSDIR%\ARM
set RVCT22BIN=%RVCT22DIR%\RVCT\Programs\2.2\349\win_32_pentium
set RVCT22INC=%RVCT22DIR%\RVCT\Data\2.2\349\include\windows
set RVCT22LIB=%RVCT22DIR%\RVCT\Data\2.2\349\lib

set ARMLMD_LICENSE_FILE=8224@ladybug1.pcs.mot.com;8224@ladybug2.pcs.mot.com;8224@beetle3.pcs.mot.com

rem - FALL THROUGH

:vc6
echo MS Visual C/C++ 6.0 environment

set VSCOMMONDIR=%COMPILERSDIR%\vc6\common
set MSDEVDIR=%VSCOMMONDIR%\MSDEV98
set MSVCDIR=%COMPILERSDIR%\vc6\vc98

set PATH=%MSDevDir%\BIN;%MSVCDir%\BIN;%VSCommonDir%\TOOLS;%PATH%
set INCLUDE=%MSVCDir%\ATL\INCLUDE;%MSVCDir%\INCLUDE;%MSVCDir%\MFC\INCLUDE;%INCLUDE%
set LIB=%MSVCDir%\LIB;%MSVCDir%\MFC\LIB;%LIB%

set LINT=%LINT% co-msc60.lnt %LINT_USER%

set MPC_TOOLSET=msvc
set MPC_TOOLSET_VERSION=6.0

goto exit

:watcom
echo Watcom C/C++ environment
SET CC_PATH=%COMPILERSDIR%\watcom
SET PATH=%CC_PATH%\BINNT;%CC_PATH%\BINW;%PATH%
SET WATCOM=%CC_PATH%
SET INCLUDE=%CC_PATH%\H\stlport;%CC_PATH%\H;%CC_PATH%\H\NT
set LIB=%CC_PATH%\lib386;%CC_PATH%\lib386\nt;%LIB%

goto exit

:vc71
echo MS Visual C/C++ 7.1 environment

call "%VS71COMNTOOLS%vsvars32.bat"

goto exit

:vc9
echo MS Visual C/C++ 9.0 environment

call "%VS90COMNTOOLS%vsvars32.bat"

goto exit


:icl
echo Intel C/C++ environment
SET CC_PATH=%WORKBIN%\compilers\icc
SET PATH=%CC_PATH%\ia32\bin;%PATH%
SET LIB=%CC_PATH%\ia32\lib;%LIB%
SET INCLUDE=%CC_PATH%\ia32\include;%INCLUDE%

set MPC_TOOLSET=icl
goto vc6

:mingw
echo GNU C/C++ environment
set CC_PATH=%COMPILERSDIR%\gcc\mingw_4.3
set PATH=%CC_PATH%\bin;%PATH%

goto exit

:arm
echo GNU C/C++ environment for ARM
rem set CC_PATH=%COMPILERSDIR%\codesourcery2005q3_2
rem set PATH=%PATH%;%CC_PATH%\bin

rem set QTDIR=D:\work\rhonda\lj\sdk\elba\qt-2.3.6

doskey mf=cd D:\work\rhonda\lj\src\mf\mfapp

goto exit

:dmc
echo Digital Mars C/C++ environment
SET CC_PATH=%COMPILERSDIR%\dmc
set PATH=%CC_PATH%\bin;%PATH%
set INCLUDE=%CC_PATH%\include;%INCLUDE%
set LIB=%CC_PATH%\lib;%LIB%

REM ~ set INCLUDE=%CC_PATH%\include;%CC_PATH%\PlatformSDK\Include;
REM ~ set LIB=%CC_PATH%\lib;%CC_PATH%\PlatformSDK\lib;

set MPC_TOOLSET=dmc
set MPC_TOOLSET_VERSION=8.42n
goto exit

:bcc
echo Borland C/C++ environment
SET CC_PATH=%COMPILERSDIR%\bcc
set PATH=%CC_PATH%\bin;%PATH%

set MPC_TOOLSET=bcc
set MPC_TOOLSET_VERSION=5.5.1

goto exit

:avr
echo Environment for Atmel AVR series of RISC microprocessors
set AVR_DIR=%COMPILERSDIR%\WinAVR
set CC_PATH=%AVR_DIR%\avr
set GCC_VER=4.1.1
set PATH=%CC_PATH%\bin;%AVR_DIR%\bin;%AVR_DIR%\utils\bin;%PATH%
set CPATH=%CC_PATH%\include;%CC_PATH%\include\avr;%CC_PATH%\include\util;%AVR_DIR%\lib\gcc\avr\4.1.1\include
set INCLUDE=%CPATH%
set LIBRARY_PATH=%CC_PATH%\lib;%LIB%

set LINT=%LINT% -i%FLEXLINT_USER_DIR% co-mingw.lnt %LINT_USER%

set MPC_TOOLSET=winavr-gcc
set MPC_TOOLSET_VERSION=4.1.1

goto exit

:ddk
echo Environment for Microsoft Device Driver Kit (DDK) development

set CC_PATH=D:\WINDDK\3790.1830

call D:\WINDDK\3790.1830\bin\setenv.bat D:\WINDDK\3790.1830 fre WXP
set INCLUDE=%CC_PATH%\inc\wnet;%CC_PATH%\inc\wxp;%CC_PATH%\inc;%CC_PATH%\inc\crt;%INCLUDE%
set LIB=%CC_PATH%\lib\wxp\i386;%CC_PATH%\lib\crt\i386

cd %WORKPATH%\rhonda\hapitouch\src

set LINT=%LINT% co-msc71.lnt %LINT_USER%
set MPC_TOOLSET=msvc
set MPC_TOOLSET_VERSION=7.1
goto exit


:tools

:exit
