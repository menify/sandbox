import os.path
import string

import MPC_Version

#//---------------------------------------------------------------------------//

def     _find_it( env ):
    return SCons.Tool.Tool( 'qt' ).exists( env )

#//---------------------------------------------------------------------------//

def     _qt_version( env ):
    
    line = os.popen(env['QT_MOC'] + ' -v').readline()
    match = re.search(r'\(Qt [0-9]+(\.[0-9]+)+\)', line)
    
    if match:
        return MPC_Version( match.group() )
    
    return ''

#//---------------------------------------------------------------------------//

def     Qt4AddModules( env, modules ):
    
    target_platform = env['PLATFORM']   ## TODO Must be replaced with MPC_TARGET_PLATFORM
    
    if target_platform == 'win32':
        env.Append( LIBS = ['user32', 'kernel32', 'ole32', 'shell32', 'gdi32', 'imm32', 'uuid', 'comdlg32', 'ws2_32', 'winspool'] )
    
    cpp_path = os.path.join('$QTDIR', 'include')
    
    env.AppendUnique( QT_CPPPATH = [ (os.path.join( cpp_path, inc ) ) for inc in modules ] )
    env.AppendUnique( QT_LIB = [ mod for mod in modules ] )
    
    if 'Qt3Support' in modules:
       env.AppendUnique( CPPDEFINES = ['QT3_SUPPORT'] )
    
    try:
        debug = int(env.subst('$QT_DEBUG'))
    except ValueError:
        debug = 0
    
    if debug:
        # Check if we are in windows. The libraries end with a different suffix depending on if its windows or not.
        if(target_platform == "win32"):
            env.AppendUnique(LIBS =  [mod+"d" for mod in modules]) # Add the debug libs to be linked
        else:
            env.AppendUnique(LIBS =  [mod+"_debug" for mod in modules]) # Add the debug libs to be linked
    else:
        if(target_platform == "win32"):
            env.AppendUnique(LIBS =  [mod+"" for mod in modules]) # Add the release libs to be linked
        else:
            env.AppendUnique(LIBS =  [mod for mod in modules]) # Add the release libs to be linked

from SCons.Script.SConscript import SConsEnvironment
SConsEnvironment.QtAddModules = Qt4AddModules

#//---------------------------------------------------------------------------//

def     generate(env):
    
    SCons.Tool.Tool( 'qt' )( env )
    
    qt_ver = _qt_version( env )
    env['QT_VERSION'] = qt_ver
    
    if qt_ver == '4':
        env.SetDefault(
                QT_QRC = os.path.join('$QT_BINPATH','rcc'),
                QT_QRCIMPLSUFFIX = '_qrc.cpp',
                QT_QRCSUFFIX = '.qrc',
                
                QT_QRCCOM = [ CLVar('$QT_QRC $QT_QRCDECLFLAGS $SOURCE -name ${SOURCE.filebase} -o ${TARGETS[0]}') ],
            )
        
        qrcBld = Builder(action=SCons.Action.Action('$QT_QRCCOM', '$QT_QRCCOMSTR'),
                         suffix='$QT_QRCIMPLSUFFIX',
                         src_suffix='$QT_QRCSUFFIX')
        
        env['BUILDERS']['Qrc'] = qrcBld
        
        static_obj, shared_obj = SCons.Tool.createObjBuilders( env )
        static_obj.src_builder.append('Qrc')
        shared_obj.src_builder.append('Qrc')
    
        env[ 'QT_LIB' ] = []
        env.QtAddModules( ['QtCore', 'QtGui' ] )

#//---------------------------------------------------------------------------//

def exists(env):
    return _find_it( env )
