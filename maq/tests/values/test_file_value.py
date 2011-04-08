import io
import sys
import os.path
import tempfile
import pickle

sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'utils') )
sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'values') )

from aql_logging import logDebug, logError
from aql_file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp

#//===========================================================================//

def   test():
  with io.BytesIO() as file:
    with tempfile.NamedTemporaryFile( delete = False ) as temp_file:
      
      temp_file.write( '1234567890\n1234567890'.encode() )
      temp_file.flush()
      
      temp_file_name = FileName( temp_file.name )
      
      temp_file_value = FileValue( temp_file_name )
      logDebug( "temp_file_value: %s, %s", temp_file_value, temp_file_value.content )
      
      temp_file.close()
      os.remove( temp_file_name )
      
      saver = pickle.Pickler( file, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( temp_file_value, ) )
      
      file.seek(0)
      
      loader = pickle.Unpickler( file )
      loaded_values = loader.load()
      value = loaded_values[0]
      logDebug( "value: %s, %s", value, value.content )
      
      new_value = FileValue( value )
      
      logDebug( "new_value: %s, %s", new_value, new_value.content )
      
      logDebug( "new_value == value: %s", new_value == value )
      logDebug( "new_value.content == value.content: %s", new_value.content == value.content )
      logDebug( "value.content == new_value.content: %s", value.content == new_value.content )
      

if __name__ == "__main__":
  
  logError( "test logging" )
  test()


import sys
import re
import os.path
import unittest
import urllib2
import xml.parsers.expat
import binascii
import uuid
import string
import datetime

_CURRENT_TASK_ID = 0
_NEXT_TASK_ID = 12345679

#//=======================================================//

class XmlNode (object):
  __slots__ = ('name', 'attrs', 'children', 'text' )
  
  def   __init__(self, name, attrs ):
    self.name = name
    self.attrs = attrs
    self.children = []
    self.text = ''
  
  #//-------------------------------------------------------//
  
  def   find( self, name ):
    if self.name == name:
      return self
    
    for node in self.children:
      node = node.find( name )
      if node is not None:
        return node
    
    return None
    
  #//-------------------------------------------------------//
  
  def   findAll( self, name, found_nodes = None ):
    
    if found_nodes is None:
      found_nodes = []
    
    if self.name == name:
      found_nodes.append( self )
    
    else:
      for node in self.children:
        node.findAll( name, found_nodes )
    
    return found_nodes
    
  #//-------------------------------------------------------//
  
  def __iter__(self):
      nodes = [self]
      next_nodes = []
      
      while nodes:
        for node in nodes:
          next_nodes += node.children
          yield node
        
        nodes = next_nodes
        next_nodes = []
  
  #//-------------------------------------------------------//
  
  def dump( self, indent = 0 ):
    print " " * indent + "<" + self.name + ' ' + str(self.attrs) + '>'
    for node in self.children:
      node.dump( indent + 2 )
    print " " * indent + "</" + self.name + '>'

#//===========================================================================//

def  _verifyXml( xml_text ):
  try:
    xml.parsers.expat.ParserCreate().Parse( xml_text, True )
  except:
    print "\nError: Invalid XML request."
    raise

#//===========================================================================//

def   _sendRequest( cem_url, data, verbose, session_id = "" ):
  global _NEXT_TASK_ID
  global _CURRENT_TASK_ID
  
  req = urllib2.Request( cem_url )
  
  req.add_header( 'Content-Type', 'text/xml')
  
  if session_id:
    session_id = ' uiCookie="%s"' % session_id
  
  data = '<?xml version="1.0"?>' + \
          '<BAMTask timeout="600" id="%s"%s>' % (_NEXT_TASK_ID, session_id) + \
            data + \
          '</BAMTask>'
  
  _CURRENT_TASK_ID = _NEXT_TASK_ID
  _NEXT_TASK_ID += 1
  
  req.add_data( data )
  
  if verbose:
    print ">" * 64
    print "Sending request:"
    print data
    print
  
  try:
    response = urllib2.urlopen( req, timeout = 600 )
  except TypeError:
    response = urllib2.urlopen( req )
  
  return response

#//=======================================================//

def   _readXmlResponse( output, verbose ):
  
  stack = []
  root_node = []
  
  def startElement( name, attrs, stack = stack ):
    
    node = XmlNode( name, attrs )
    
    try:
      parent_node = stack[-1]
      parent_node.children.append( node )
    except IndexError:
      pass
    
    stack.append( node )
  
  def endElement(name, stack = stack, root_node = root_node):
    if len(stack) == 1:
      root_node.append( stack[0] )
    del stack[-1]
  
  p = xml.parsers.expat.ParserCreate()
  p.StartElementHandler = startElement
  p.EndElementHandler = endElement
  
  #//-------------------------------------------------------//
  
  xml_response_prefix = '<?xml '
  
  xml_response = ''
  xml_response_prefix_found = False
  
  while True:
    xml_text = output.read(1)
    
    if xml_text not in string.printable:
      xml_text = re.escape( binascii.hexlify( xml_text ) )
    
    xml_response = xml_response + xml_text
    
    if len(xml_response) >= len(xml_response_prefix):
      if not xml_response_prefix_found:
        if xml_response.startswith( xml_response_prefix ):
          xml_response_prefix_found = True
          p.Parse( xml_response, False )
        else:
          xml_response = xml_response[1:]
      
      else:
        p.Parse( xml_text, False )
        if root_node:
          root_node = root_node[0]
          root_node.text = xml_response
        
          if verbose:
            print "<" * 64
            print "Response:"
            print xml_response
            print
          
          return root_node

#//=======================================================//

def   _getSessionId( cem_url, login, password, verbose ):
  
  global _NEXT_TASK_ID
  global _CURRENT_TASK_ID
  
  data = '<Login>' + \
              '<Users>' + \
                '<User requestId="%s" name="%s" password="%s" authenticationType="basic" hostIp="1.1.1.1"/>' % (_NEXT_TASK_ID, login, password) + \
              '</Users>' + \
            '</Login>'
  
  http_response = _sendRequest( cem_url, data, verbose )
  
  xml_node = _readXmlResponse( http_response, verbose )
  if xml_node is None:
    raise UserWarning("Invalid response")
  
  if int(xml_node.attrs.get('id', -1)) != _CURRENT_TASK_ID:
    raise UserWarning("Incorrect id")
  
  try:
    status_node = xml_node.find('bam:Status')
    
    if status_node is None:
      raise UserWarning("No 'Status' element found")
    
    if int(status_node.attrs.get('id', -1)) != 0:
      raise UserWarning("Incorrect login/password")
    
    if int(status_node.attrs.get('requestId', -1)) != _CURRENT_TASK_ID:
      raise UserWarning("Incorrect requestId")
    
    user_node = xml_node.find('bam:User')
    if user_node is None:
      raise UserWarning("No 'User' element found")
    
    if int(user_node.attrs.get('requestId', -1)) != _CURRENT_TASK_ID:
      raise UserWarning("Incorrect requestId")
    
    return user_node.attrs['sessionId']
    
  except BaseException, e:
    if isinstance( e, UserWarning ):
      raise
      
    raise UserWarning("Invalid XML response")

#//=======================================================//

class _Connection( object ):
  __slots__ = ( 'handle', 'cem_url', 'session_id' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, cem_url, login, password, verbose = True ):
    session_id = _getSessionId( cem_url, login, password, verbose )
    
    handle = _sendRequest( cem_url, '<Connect><CemSystem/></Connect>', verbose, session_id )
    
    while True:
      xml_node = _readXmlResponse( handle, verbose )
      if xml_node is not None:
        node = xml_node.find( 'bam:SessionConnected' )
        if (node is not None) and (node.attrs.get('sessionId', '0') == session_id ):
          break
    
    self.handle = handle
    self.cem_url = cem_url
    self.session_id = session_id
  
  #//-------------------------------------------------------//
  
  def   send( self, request, verbose = True):
    return _sendRequest( self.cem_url, request, verbose, self.session_id )
  
  #//-------------------------------------------------------//
  
  def   read( self, verbose = True):
    return _readXmlResponse( self.handle, verbose )
  
  #//-------------------------------------------------------//
  
  def   recv( self, verbose = True):
    global _CURRENT_TASK_ID
    task_respond_id = str(_CURRENT_TASK_ID)
    
    while True:
      node = self.read( verbose )
      if node is not None:
        node = node.find( 'bam:BAMTask' )
        
        if (node is not None) and (node.attrs.get('id') == task_respond_id):
          return node
  
  #//-------------------------------------------------------//
  
  def   close( self ):
    self.handle.close()

#//===========================================================================//

def   _findErrorCodesFile( start_dir ):
  abs_path = os.path.abspath( start_dir )
  if not os.path.isdir(abs_path):
    abs_path = os.path.dirname( abs_path )
  
  components_path = 'components'
  pos = abs_path.find(components_path)
  if (pos != -1) or abs_path.endswith( components_path ):
    components_path = abs_path[:pos + len(components_path) ]
    error_codes_file = os.path.join( components_path, 'common','sspg','c4cb','ErrorCodes','ErrorCodes.csv' )
    if os.path.isfile(error_codes_file):
      return error_codes_file
  
  for root, dirs, files in os.walk( abs_path ):
      if 'ErrorCodes.csv' in files:
        error_codes_file = os.path.join( root, 'ErrorCodes.csv' )
        print "+ error_codes_file:", error_codes_file
        return error_codes_file
      
      if '.svn' in dirs:
          dirs.remove('.svn')  # don't visit .svn directories
  
  return None


#//===========================================================================//

def   _loadErrorCodesFile( error_codes_file ):
  
  error_code_id_re = re.compile(r"^[A-Z]+[A-Z0-9_]*$")
  
  ids = {}
  for l in open( error_codes_file ):
    values = l.split(',')
    try:
      error_code_value = int( values[0].strip(), 0 )
      error_code_id = values[1].strip()
      if error_code_id_re.match( error_code_id ):
        ids[ error_code_id ] = error_code_value
    except:
      pass
  
  return ids

#//===========================================================================//

def _importErrorCodes( error_codes_file ):
    if error_codes_file is None:
      error_codes_file = _findErrorCodesFile( __file__ ) or _findErrorCodesFile( os.getcwd() )
    
    if error_codes_file is None:
      print "Error: ErrorCodes.csv file has been not found"
      return False
      
    ids = _loadErrorCodesFile( error_codes_file )
    globals().update( ids )
    
    return True

#//===========================================================================//

def   _getServerName():
  return 'kb_' + uuid.uuid4().hex[:12]

#//===========================================================================//

def   _incrementIP( ip ):
    def _inc( n ):
      n = int(n) + 1
      if n > 254: n = 1
      return str(n)
    
    return '.'.join( map( _inc, ip.split('.') ) )

#//===========================================================================//

class _GlobalSettings( object ):
  def   __init__(self):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-H", "--cem_url", dest="cem_url",
                      help = "IP address or name of CEM", metavar = "host")
    
    parser.add_option("-u", "--cem_login", dest="cem_login",
                      help = "User's login", metavar = "LOGIN")
    
    parser.add_option("-p", "--cem_password", dest = "cem_password",
                      help = "User's password", metavar = "PASSWORD")
    
    parser.add_option("-i", "--interfaces", dest = "interfaces",
                      help = "IP addresses which can be used to create new interfaces", metavar = "IP[,IP[,IP]...]")
    
    parser.add_option("-g", "--default_gateway", dest = "default_gateway",
                      help = "Default gateway for CIFS servers", metavar = "IP")
    
    parser.add_option("-d", "--cifs_domain", dest = "cifs_domain",
                      help = "CIFS domain", metavar = "DOMAIN_NAME")
    
    parser.add_option("-s", "--cifs_admin_user", dest = "cifs_admin_user",
                      help = "CIFS user", metavar = "LOGIN")
    
    parser.add_option("-w", "--cifs_admin_password", dest = "cifs_admin_password",
                      help = "CIFS password", metavar = "PASSWORD")
    
    parser.add_option("-o", "--cifs_nonadmin_user", dest = "cifs_nonadmin_user",
                      help = "CIFS user", metavar = "LOGIN")
    
    parser.add_option("-r", "--cifs_nonadmin_password", dest = "cifs_nonadmin_password",
                      help = "CIFS password", metavar = "PASSWORD")
    
    parser.add_option("-n", "--cifs_dns", dest = "cifs_dns",
                      help = "CIFS domain DNS server IPs", metavar = "IP")
    
    parser.add_option("-t", "--cifs_ntp", dest = "cifs_ntp",
                      help = "CIFS domain time server", metavar = "IP or NAME")
    
    parser.add_option("-e", "--error_codes_file", dest = "error_codes_file",
                      help = "Path to ErrorCodes.csv file", metavar = "FILE PATH")
    
    parser.add_option("-c", "--config", dest = "config",
                      help = "Path to config file", metavar = "FILE PATH")
    
    parser.add_option("-x", "--tests", dest = "tests",
                      help = "List of tests which should be executed", metavar = "TESTS")
    
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                      help = "Quiet mode", default = True )
    
    parser.add_option("-k", "--cleanup", action="store_true", dest="cleanup",
                      help = "Clean-up existing instances", default = False )
    
    (options, args) = parser.parse_args()
    print_usage = False
    
    settings = {}
    
    if options.config is not None:
      if not os.path.isfile(options.config):
        print "Error: Config file doesn't exist."
        print_usage = True
      else:
        execfile( options.config, {}, settings )
    
    for opt,value in options.__dict__.iteritems():
      if (value is not None) or (opt not in settings):
        settings[ opt ] = value
    
    if settings['cem_url'] is None:
      print "Error: CEM URL is not specified"
      print_usage = True
    
    elif settings['cem_login'] is None:
      print "Error: User's login is not specified"
      print_usage = True
    
    elif settings['cem_password'] is None:
      print "Error: User's login is not specified"
      print_usage = True
    
    elif settings['interfaces'] is None:
      print "Error: IP addresses of interfaces are not specified"
      print_usage = True
    
    elif settings['default_gateway'] is None:
      print "Error: Default gateway is not specified"
      print_usage = True
    
    elif settings['cifs_domain'] is None:
      print "Error: CIFS domain is not specified"
      print_usage = True
    
    elif settings['cifs_admin_user'] is None:
      print "Error: CIFS admin user is not specified"
    
      print_usage = True
    elif settings['cifs_admin_password'] is None:
      print "Error: CIFS admin password is not specified"
      print_usage = True
    
    elif settings['cifs_nonadmin_user'] is None:
      print "Error: CIFS non-admin user is not specified"
      print_usage = True
    
    elif settings['cifs_nonadmin_password'] is None:
      print "Error: CIFS non-admin password is not specified"
      print_usage = True
    
    elif settings['cifs_dns'] is None:
      print "Error: CIFS DNS server is not specified"
      print_usage = True
    
    elif settings['cifs_ntp'] is None:
      print "Error: CIFS domain NTP is not specified"
      print_usage = True
    
    if not print_usage:
      print_usage = not _importErrorCodes( settings['error_codes_file'] )
    
    if print_usage:
      parser.print_help()
      exit()
    
    if not isinstance( settings['interfaces'], (list, tuple) ):
      settings['interfaces'] = settings['interfaces'].split(',')
    
    tests = settings['tests']
    if tests is None:
      settings['tests'] = []
    else:
      if not isinstance( tests, (list, tuple) ):
        settings['tests'] = tests.split(',')
    
    self.__dict__ = settings

class CemError( Exception ):
  def   __init__(self, status, msg ):
    super( CemError, self ).__init__( msg )
    self.status = status

#//===========================================================================//

class BaseSettings( object ):
  
  ignore_attr = tuple()
  
  def   __init__(self, node = None ):
    if node is None:
      return
    
    for attr, node_name in self.attr_map.iteritems():
      try:
        value = node.attrs[ node_name ]
        if node_name in ( 'interfaceIds', 'serverId', 'routeIds' ):
          value = filter( None, value.split(',') )
          
        
        try:
          value = int(value)
        except (TypeError, ValueError):
          pass
        
        setattr( self, attr, value )
      except KeyError:
        pass

  
  #//-------------------------------------------------------//
  
  def   __str__(self):
    s = []
    
    for attr, node_name in self.attr_map.iteritems():
      try:
        value = getattr( self, attr )
        if isinstance(value, (list, tuple) ):
          value = ",".join( value )
        
        s.append( '{node_name}="{value}"'.format( node_name = node_name, value = value ) )
      except AttributeError:
        pass
    
    s = ' '.join( s )
    s = '<{node_name}s><{node_name} requestId="2233" {instance}/></{node_name}s>'.format( node_name = self.node_name, instance = s )
    
    return s
  
  #//-------------------------------------------------------//
  
  def     __repr__(self):
    return str(self)
  
  #//-------------------------------------------------------//
  
  def   __eq__(self, other ):
    assert( type(self) is type(other) )
    
    result = False
    
    for attr in self.__slots__:
      if attr in self.ignore_attr:
          continue
      
      if hasattr( other, attr ):
        if not hasattr( self, attr):
          print "No attribute '%s' in '%s'" % (attr, self )
          return False
        
        value = getattr(self, attr)
        if isinstance( value, (list, tuple) ):  value.sort()
        
        other_value = getattr( other, attr )
        if isinstance( other_value, (list, tuple) ):  other_value.sort()
        
        if attr == 'cifs_domain':
          value = value.lower()
          other_value = other_value.lower()
        
        if value != other_value:
          print "Attribute '%s' is different ('%s' != '%s')" % (attr, value, other_value )
          return False
        result = True
    
    return result

  #//-------------------------------------------------------//
  
    def   __ne__(self, other ):
      return not self.__eq__( other )
  
  #//-------------------------------------------------------//
  
  def   clone( self ):
    other = type(self)()
    for slot in self.__slots__:
      try:
        setattr( other, slot, getattr( self, slot ) )
      except AttributeError:
        pass
    
    return other

#//===========================================================================//

class InterfaceSettings( BaseSettings ):
  
  node_name = 'Interface'
  
  attr_map = {
    'id':           'id',
    'name':         'name',
    'ip':           'ipAddress',
    'netmask':      'netmask',
    'gateway':      'gateway',
    'vlan_id':      'VLANId',
    'device':       'device',
    'mac':          'interfaceMACAddr',
    'container_id': 'serverContainerId',
    'server_ids':   'serverId',
  }
  
  ignore_attr = ( 'mac' )
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class FileServerSettings( BaseSettings ):
  
  node_name = 'SharedFolderServer'
  
  attr_map = {
    'id'   :            'id',
    'name' :            'serverName',
    'container_id' :    'serverContainerId',
    'interface_ids' :   'interfaceIds',
    'is_cifs' :         'enableCIFS',
    'is_nfs' :          'enableNFS',
    'cifs_domain' :     'cifsDomName',
    'cifs_org_unit' :   'cifsOrgUnit',
    'cifs_user' :       'cifsDomUser',
    'cifs_password' :   'cifsDomPwd',
   }
  
  ignore_attr = ( 'cifs_user', 'cifs_password', 'cifs_org_unit' )
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class IscsiServerSettings( BaseSettings ):
  
  node_name = 'ISCSIServer'
  
  attr_map = {
    'id'   :          'id',
    'name' :          'serverName',
    'container_id' :  'serverContainerId',
    'interface_ids' : 'interfaceIds',
    'iqn' :           'targetIqn',
   }
  
  ignore_attr = ( 'iqn' )
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class ContainerSettings( BaseSettings ):
  
  node_name = 'ServerContainer'
  
  attr_map = {
    'id'   :          'id',
    'name' :          'name',
    'home_sp_id' :    'homeSPId',
    'current_sp_id' : 'currentSPId',
    'route_ids' :     'routeIds',
   }
  
  ignore_attr = ( 'home_sp_id', 'current_sp_id' )
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class EthernetPortSettings( BaseSettings ):
  
  node_name = 'EthernetPort'
  
  attr_map = {
    'id'   :        'id',
    'name' :        'name',
    'port_id' :     'portId',
    'port_speed' :  'portSpeed',
    'mtu' :         'mtuSize',
   }
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class RouteSettings( BaseSettings ):
  
  node_name = 'Route'
  
  attr_map = {
    'id'   :          'id',
    'container_id' :  'serverContainerId',
    'type' :          'type',
    'gateway' :       'gateway',
    'destination' :   'destination',
    'netmask' :       'netmask',
    'interface_id' :  'interfaceId',
   }
  
  ignore_attr = ( 'id', 'interface_id' )
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class DnsServerSettings( BaseSettings ):
  
  node_name = 'DNSServer'
  
  attr_map = {
    'id'   :          'id',
    'domain' :        'domain',
    'ip' :            'ipAddress',
   }
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class NtpServerSettings( BaseSettings ):
  
  node_name = 'NTPServer'
  
  __slots__ = ( 'id', 'addresses' )
  
  def   __init__(self, node = None ):
    if node is None:
      return
    
    value = node.attrs[ 'id' ]
    if value is not None:
      try:
        value = int(value)
      except (TypeError, ValueError):
        pass
      
    self.id = value
    
    #---
    
    self.addresses = []
    
    for address_nodes in node.children:
      if address_nodes.name == 'bam:Address':
        self.addresses.append( address_nodes.attrs['value'] )
  
  #//-------------------------------------------------------//
  
  def   __str__(self):
    
    attributes = []
    addresses = []
    
    if hasattr(self, 'id'):
      attributes.append( 'id="%s"' % self.id )
    
    if hasattr( self, 'addresses'):
      for addr in self.addresses:
        addresses.append( '<Address value="%s"/>' % addr )
    
    attributes = ' '.join(  attributes )
    addresses = ' '.join(  addresses )
    
    s = '<{node_name}s><{node_name} requestId="2233" {attributes}>{addresses}</{node_name}></{node_name}s>'.format( node_name = self.node_name, attributes = attributes, addresses = addresses )
    
    return s
  
  #//-------------------------------------------------------//

#//===========================================================================//

class SharedFolderSettings( BaseSettings ):
  
  node_name = 'SharedFolder'
  
  attr_map = {
    'id'   :                          'id',
    'name' :                          'name',
    'description' :                   'description',
    'status' :                        'status',
    'size' :                          'size',
    'size_used' :                     'sizeUsed',
    'creation_time' :                 'creationTime',
    'last_modified_time' :            'lastModifiedTime',
    'additional_capacity' :           'maxAvailableAdditionalCapacity',
    'current_allocation' :            'currentAllocation',
    'server_id' :                     'serverId',
    'protection_schedule_id' :        'protectionScheduleId',
    'protection_schedule_paused' :    'protectionSchedulePaused',
    'protection_size' :               'protectionSize',
    'protection_size_used' :          'protectionSizeUsed',
    'protection_current_allocation' : 'protectionCurrentAllocation',
    'vp_enabled' :                    'vpEnabled',
    'vp_high_water_mark' :            'vpHighWaterMark',
    'storage_pool_id' :               'storagePoolId',
    'fs_name' :                       'fsName',
    'file_level_retention' :          'fileLevelRetention',
    'cifs_sync_writes' :              'cifsSyncWrites',
    'op_locks' :                      'opLocks',
    'file_change_notify_on_write' :   'fileChangeNotifyOnWrite',
    'file_change_notify_on_access' :  'fileChangeNotifyOnAccess',
    'file_change_directory_depth' :   'fileChangeDirectoryDepth',
    'share_type' :                    'shareType',
    'cifs_share_ids' :                'cifsShareIds',
    'nfs_share_ids' :                 'nfsShareIds',
    'replication_session_ids' :       'replicationSessionIds',
    'is_replication_destination' :    'isReplicationDestination',
    'auto_protection_adjust' :        'autoProtectionAdjust',
    'snapshot_ids' :                  'snapshotIds',
   }
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

class StoragePoolSettings( BaseSettings ):
  
  node_name = 'StoragePool'
  
  attr_map = {
    'id'   :                          'id',
    'available_size' :                'availableSize',
    'type' :                          'storagePoolType',
    'technology' :                    'technology',
    'server_id' :                     'serverId',
    'server_name' :                   'serverName',
    'total_capacity' :                'totalCapacity',
    'threshold_percent' :             'thresholdPercent',
    'subscription_in_bytes' :         'subscriptionInBytes',
    'used_size' :                     'usedSize',
   }
  
  __slots__ = tuple( attr_map.iterkeys() )

#//===========================================================================//

def _getXmlNodes( connection, request, node_name ):
  
  now = datetime.datetime.now()
  
  connection.send( request )
  response_node = connection.recv()
  status_node = response_node.find('bam:Status')
  if not status_node:
    raise EnvironmentError( "Failed to get status of the request: '%s'" % request )
  
  status = int( status_node.attrs.get('id', 0) )
  nodes = response_node.findAll( node_name )
  
  print
  print "Request time: ", (datetime.datetime.now() - now)
  print '_' * 64
  
  return (status, nodes)

#//===========================================================================//

def   _getInstances( connection, request_type, instance ):
  if isinstance( instance, type):
    instance = instance()
  
  request = "<{request_type}>{instance}</{request_type}>".format( request_type = request_type, instance = instance)
  
  status, nodes = _getXmlNodes( connection, request, 'bam:' + instance.node_name )
  
  if status != 0:
    raise CemError( status, "Request {request_type} of {node_name} has been failed with status '{status}'".format( request_type = request_type, node_name = instance.node_name, status = status ))
  
  instances = map( type(instance), nodes )
  
  return instances

#//===========================================================================//

def   _listInstances( connection, instance ):       return _getInstances( connection, 'List', instance )
def   _recommendInstances( connection, instance ):  return _getInstances( connection, 'Recommend', instance )
def   _newInstance( connection, instance ):         return _getInstances( connection, 'New', instance )[0]
def   _modifyInstance( connection, instance ):      return _getInstances( connection, 'Modify', instance )[0]
def   _deleteInstance( connection, instance ):      return _getInstances( connection, 'Delete', instance )[0]

#//===========================================================================//

def   _deleteInstances( connection, *instance_types ):
  
  for instance_type in instance_types:
    if isinstance( instance_type, type ):
      try:
        instances = _listInstances( connection, instance_type )
      except CemError:
        pass
    elif not isinstance( instance_type, (list,tuple) ):
      instances = ( instance_type, )
    else:
      instances = instance_type
    
    for instance in instances:
      try:
        _deleteInstance( connection, instance )
      except CemError:
        pass

#//===========================================================================//

def   _getInstanceIds( instances ):
  ids = []
  for instance in instances:
    ids.append( instance.id )
  
  return ids


#//===========================================================================//

def   _getPorts( connection ):
  def _isValidPort( port ):
    if hasattr( port, 'name' ) and port.name.startswith('eth'):
      try:
        int( port.name[3:] )
        return True;
      except TypeError:
        pass
    
    return False
  
  ports = filter( _isValidPort, _listInstances( connection, EthernetPortSettings ) )
  return map( lambda port: port.name, ports )

#//===========================================================================//

def   _getContainers( connection ):
  containers = _listInstances( connection, ContainerSettings )
  return map( lambda container: container.id, containers )

#//===========================================================================//

def   _addDnsServer( connection, domain, ip ):
  
  new_dns_server = DnsServerSettings()
  new_dns_server.domain = domain
  new_dns_server.ip = ip
  
  for dns_server in _listInstances( connection, DnsServerSettings ):
    if dns_server == new_dns_server:
      return
  
  _newInstance( connection, new_dns_server )

#//===========================================================================//

def   _addNtpServer( connection, settings ):
  ntp_addresses = []
  
  for ntp_server in _listInstances( connection, NtpServerSettings ):
    if hasattr(ntp_server, 'addresses'):
      ntp_addresses += ntp_server.addresses
  
  if settings.cifs_ntp not in ntp_addresses:
    ntp_server = NtpServerSettings()
    ntp_server.addresses = [ settings.cifs_ntp ]
    ntp_server.addresses += ntp_addresses
    
    _newInstance( connection, ntp_server )

#//===========================================================================//

class SanityTest(unittest.TestCase):
  
  def   __init__(self, testname, settings, connection, port_names, container_ids ):
    super(SanityTest, self).__init__(testname)
    
    self.settings = settings
    self.connection = connection
    
    self.port_names = port_names
    self.container_ids = container_ids
    self.test_instances = {}
    self.result = self.defaultTestResult()
    
    self.default_route = None
  
  #//=======================================================//
  
  def run( self, result = None ):
    if result is not None:
      self.result = result
    
    super( SanityTest, self ).run( self.result )
  
  #//=======================================================//
  
  def   createInstance( self, instance, status = 0 ):
    try:
      if not isinstance( status, (list,tuple) ):
        status = (status,)
      
      new_instance = _newInstance( self.connection, instance )
      self.test_instances[ new_instance.id ] = new_instance
      
      assert( 0 in status )
      self.assertEqual( new_instance, instance )
      
      return new_instance
    
    except CemError, e:
      assert( e.status in status )
      return None
  
  #//=======================================================//
  
  def   modifyInstance( self, instance, status = 0 ):
    
    has_instance_id = True
    
    try:
      if not isinstance( status, (list,tuple) ):
        status = (status,)
      
      try:
        del self.test_instances[ instance.id ]
      except (NameError, KeyError):
        has_instance_id = False
      
      modified_instance = _modifyInstance( self.connection, instance )
      self.test_instances[ modified_instance.id ] = modified_instance
      assert( 0 in status )
      self.assertEqual( modified_instance, instance )
      return modified_instance
    
    except CemError, e:
      if has_instance_id:
        self.test_instances[ instance.id ] = instance
      assert( e.status in status )
      return None

  
  #//=======================================================//
  
  def   deleteInstance( self, instance, status = 0 ):
    try:
      if not isinstance( status, (list,tuple) ):
        status = (status,)
      
      deleted_instance = _deleteInstance( self.connection, instance )
      try:
        del self.test_instances[ deleted_instance.id ]
      except (NameError, KeyError):
        pass
      
      assert( 0 in status )
      self.assertEqual( deleted_instance.id, instance.id )
      return deleted_instance
    
    except CemError, e:
      assert( e.status in status )
      return None
  
  #//=======================================================//
  
  def   listInstances( self, type ):
    return _listInstances( self.connection, type )
  
  #//=======================================================//
  
  def   deleteInstances( self, instances ):
    for instance in instances:
        self.deleteInstance( instance )
  
  #//=======================================================//
  
  def   tearDown(self):
    try:
      self.deleteInstances( list( self.test_instances.itervalues() ) )
      
      default_route = self._getDefaultRoute()
      if (default_route is not None) and ((self.default_route is None) or (default_route.gateway != self.default_route.gateway)):
        self.deleteInstance( default_route )
      
      if (self.default_route is not None) and ((default_route is None) or (default_route.gateway != self.default_route.gateway)):
        self.createInstance( self.default_route )
    
    finally:
      if not self.result.wasSuccessful():
        self.result.stop()
    
  #//===========================================================================//
  
  def   setUp(self):
    if not self.result.wasSuccessful():
      self.result.stop()
    
    print
    print "*" * 64
    print "* TestCase:", self.id()
    print "*" * 64
    
    self.default_route = self._getDefaultRoute()
    
    self.assert_( len(self.port_names) > 0 )
    self.assert_( len(self.container_ids) > 0 )
  
  #//=======================================================//
  
  def   createInterfaces( self, num_interfaces = -1, create_default_gateway = True, addresses = None ):
    
    container_id = self.container_ids[0]
    device = self.port_names[0]
    interfaces = []
    
    if addresses is None:
      addresses = self.settings.interfaces
    elif not isinstance( addresses, (list, tuple) ):
      addresses = ( addresses, )
    
    if num_interfaces != -1:
      addresses = addresses[:num_interfaces]
    
    for ip in addresses:
      
      interface = InterfaceSettings()
      interface.ip = ip
      interface.container_id = container_id
      interface.netmask = "255.255.255.0"
      interface.device = device
      if create_default_gateway:
        interface.gateway = self.settings.default_gateway
      
      interfaces.append( self.createInstance( interface ) )
    
    return interfaces
  
  #//=======================================================//
  
  def testInterfaces(self):
    
    #//-------------------------------------------------------//
    #// new interface
    
    new_interface = self.createInterfaces( 1 )[0]
    
    #//-------------------------------------------------------//
    #// modify interface
    
    if len(self.port_names) > 1:
      new_interface.device = self.port_names[1]
    
    if len(self.settings.interfaces) > 1:
      new_interface.ip = self.settings.interfaces[1]
    
    new_interface.vlan_id = 2
    
    modified_interface = self.modifyInstance( new_interface )
    
    if len(self.port_names) > 1:
      modified_interface.device = self.port_names[0]
    
    new_interface.vlan_id = 0
    modified_interface = self.modifyInstance( modified_interface )
    
    #//-------------------------------------------------------//
    #// delete interface
    
    self.deleteInstance( modified_interface )
  
  #//=======================================================//
  
  def testInterfaces_ForErrors(self):
    
    new_interface = InterfaceSettings()
    new_interface.container_id = self.container_ids[0]
    new_interface.ip = self.settings.interfaces[0]
    new_interface.device = self.port_names[0]
    new_interface.netmask = "255.255.255.0"
    
    #//-------------------------------------------------------//
    #// Check invalid container
    
    new_interface.container_id = ""
    self.createInstance( new_interface, [INVALID_PARAMETER, FAILED, UNKNOWN_ERR] )
    
    new_interface.container_id = "container_invalid_id"
    self.createInstance( new_interface, [INVALID_PARAMETER, FAILED, UNKNOWN_ERR] )
    
    new_interface.container_id = self.container_ids[0]
    
    #//-------------------------------------------------------//
    #// Check invalid IP
    
    new_interface.ip = "1234153"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_IP_ADDR_ERR )
    
    new_interface.ip = "0.0.0.0"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_IP_ADDR_ERR )
    
    new_interface.ip = "255.255.255.255"
    self.createInstance( new_interface, INVALID_PARAMETER )
    
    new_interface.ip = self.settings.interfaces[0]
    
    #//-------------------------------------------------------//
    #// Check invalid netmask
    
    new_interface.netmask = "0"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_NETMASK_ERR )
    
    new_interface.netmask = "0.0.0.0"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_NETMASK_ERR )
    
    new_interface.netmask = "255.255.255.0"
    
    #//-------------------------------------------------------//
    #// Check invalid device
    
    new_interface.device = "port1"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_DEVICE_ERR )
    
    new_interface.device = self.port_names[0] + self.port_names[0]
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_DEVICE_ERR )
    
    new_interface.device = "eth222"
    self.createInstance( new_interface, NASSERVICES_INTERFACE_INVALID_DEVICE_ERR )
    
    #//-------------------------------------------------------//
    #// Check invalid interface id
    new_interface = InterfaceSettings()
    new_interface.id = "interface_invalid_id"
    
    self.modifyInstance( new_interface, INVALID_PARAMETER )
    self.deleteInstance( new_interface, INVALID_PARAMETER )
    
    #//-------------------------------------------------------//
    #// Check invalid gateway
    
    new_interface = InterfaceSettings()
    new_interface.container_id = self.container_ids[0]
    new_interface.ip = self.settings.interfaces[0]
    new_interface.device = self.port_names[0]
    new_interface.netmask = "255.255.255.0"
    
    invalid_gateway = _incrementIP( self.settings.default_gateway )
    new_interface.gateway = invalid_gateway
    
    self.createInstance( new_interface, NASSERVICES_ROUTE_GATEWAY_UNREACHABLE_ERR )
    interfaces = self.listInstances( InterfaceSettings )
    for interface in interfaces:
      self.assertNotEqual( interface.ip, new_interface.ip )
    
    new_interface.gateway = self.settings.default_gateway
    
    new_interface = self.createInstance( new_interface )
    new_interface.gateway = invalid_gateway
    self.modifyInstance( new_interface, NASSERVICES_ROUTE_GATEWAY_UNREACHABLE_ERR )
    
    self.deleteInstance( new_interface )
    
  #//=======================================================//
  
  def testIscsiServers_1(self):
    
    #//-------------------------------------------------------//
    #// new ISCSI server
    
    iscsi_server = IscsiServerSettings()
    iscsi_server.name = _getServerName()
    iscsi_server.container_id = self.container_ids[0]
    
    new_iscsi_server = self.createInstance( iscsi_server )
    
    #//-------------------------------------------------------//
    #// modify ISCSI server
    
    interfaces = self.createInterfaces( 2 )
    
    new_iscsi_server.interface_ids = _getInstanceIds( interfaces )
    modified_iscsi_server = self.modifyInstance( new_iscsi_server )
    
    #//-------------------------------------------------------//
    #// delete ISCSI server
    
    self.deleteInstance( modified_iscsi_server )
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testIscsiServers_2(self):
    
    #//-------------------------------------------------------//
    #// new ISCSI server
    
    
    iscsi_server = IscsiServerSettings()
    iscsi_server.name = _getServerName()
    iscsi_server.container_id = self.container_ids[0]
    interfaces = self.createInterfaces( 2 )
    iscsi_server.interface_ids = _getInstanceIds( interfaces )
    
    new_iscsi_server = self.createInstance( iscsi_server )
    
    #//-------------------------------------------------------//
    #// modify ISCSI server
    
    if len(self.port_names) > 1:
      interface = InterfaceSettings()
      interface.id = new_iscsi_server.interface_ids[0]
      interface.device = self.port_names[1]
      
      interface = self.modifyInstance( interface )
      
      interface.device = self.port_names[0]
      interface = self.modifyInstance( interface )

    
    #//-------------------------------------------------------//
    #// delete ISCSI server
    
    self.deleteInstance( new_iscsi_server )
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testIscsiServers_DifferentInterfaceContainers(self):
    
    #//-------------------------------------------------------//
    #// new ISCSI server
    
    ips = self.settings.interfaces
    container_ids = self.container_ids
    device = self.port_names[0]
    
    if (len(ips) < 2) or (len(container_ids) < 2):
      return
    
    interface = InterfaceSettings()
    interface.ip = ips[0]
    interface.container_id = container_ids[0]
    interface.netmask = "255.255.255.0"
    interface.device = device
    
    interface_1 = self.createInstance( interface )
    
    interface.ip =ips[1]
    interface.container_id = container_ids[1]
    interface_2 = self.createInstance( interface )
    
    interfaces = [interface_1, interface_2]
    
    iscsi_server = IscsiServerSettings()
    iscsi_server.name = _getServerName()
    iscsi_server.container_id = self.container_ids[0]
    iscsi_server.interface_ids = _getInstanceIds( interfaces )
    
    self.createInstance( iscsi_server, INVALID_PARAMETER )
    
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testIscsiServers_ForErrors(self):
    
    iscsi_server = IscsiServerSettings()
    iscsi_server.name = _getServerName()
    iscsi_server.container_id = self.container_ids[0]
    
    #//-------------------------------------------------------//
    #// Check invalid container id
    
    test_iscsi_server = iscsi_server.clone()
    
    test_iscsi_server.container_id = ""
    self.createInstance( test_iscsi_server, INVALID_PARAMETER )
    
    test_iscsi_server.container_id = "container_invalid_id"
    self.createInstance( test_iscsi_server, INVALID_PARAMETER )
    
    #//-------------------------------------------------------//
    #// Check invalid name
    test_iscsi_server = iscsi_server.clone()
    
    test_iscsi_server.name = ""
    self.createInstance( test_iscsi_server, NASSERVICES_ISCSISERVER_INVALID_NAME_ERR )
  
    test_iscsi_server.name = "a" * 300
    self.createInstance( test_iscsi_server, NASSERVICES_ISCSISERVER_INVALID_NAME_ERR )
    
    test_iscsi_server.name = "a b"
    self.createInstance( test_iscsi_server, NASSERVICES_ISCSISERVER_INVALID_NAME_ERR )
    
    test_iscsi_server.name = iscsi_server.name
    
    new_iscsi_server = self.createInstance( iscsi_server )
    self.createInstance( iscsi_server, NASSERVICES_ISCSISERVER_NAME_ALREADY_IN_USE_ERR )
    
    self.deleteInstance( new_iscsi_server )
    
    #//-------------------------------------------------------//
    #// Check invalid interface
    test_iscsi_server = iscsi_server.clone()
    
    test_iscsi_server.interface_ids = ['interface_invalid_id']
    self.createInstance( test_iscsi_server, INVALID_PARAMETER )
    
    interfaces = self.createInterfaces( 3 )
    
    interface_ids = _getInstanceIds( interfaces )
    
    if len(interface_ids) > 2:
      test_iscsi_server.interface_ids = interface_ids
      self.createInstance( test_iscsi_server, NASSERVICES_ISCSISERVER_TOO_MANY_INTERFACES_ERR )
    
    new_iscsi_server = self.createInstance( iscsi_server )
    
    new_iscsi_server.interface_ids = ['interface_invalid_id']
    self.modifyInstance( new_iscsi_server, INVALID_PARAMETER )
    
    if len(interface_ids) > 2:
      new_iscsi_server.interface_ids = interface_ids
      self.modifyInstance( new_iscsi_server, NASSERVICES_ISCSISERVER_TOO_MANY_INTERFACES_ERR )
    
    self.deleteInstance( new_iscsi_server )
    
    self.deleteInstances( interfaces )
    
    #//-------------------------------------------------------//
    #// Check invalid server id
    test_iscsi_server = IscsiServerSettings()
    test_iscsi_server.id = "iscsi_server_invalid_id"
    
    self.modifyInstance( test_iscsi_server, INVALID_PARAMETER )
    self.deleteInstance( test_iscsi_server, INVALID_PARAMETER )
    
  #//=======================================================//
  
  def testNfsServer_1(self):
    
    #//-------------------------------------------------------//
    #// new file server
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    
    new_file_server = self.createInstance( file_server )
    
    #//-------------------------------------------------------//
    #// modify file server
    
    new_file_server.is_nfs = 'true'
    interfaces = self.createInterfaces( 1 )
    new_file_server.interface_ids = _getInstanceIds( interfaces )
    modified_file_server = self.modifyInstance( new_file_server )
    
    #//-------------------------------------------------------//
    #// delete file server
    
    self.deleteInstance( modified_file_server )
    self.deleteInstances( interfaces )
    
  #//=======================================================//
  
  def testNfsServer_2(self):
    
    #//-------------------------------------------------------//
    #// new file server
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    interfaces = self.createInterfaces( 1 )
    file_server.interface_ids = _getInstanceIds( interfaces )
    
    new_file_server = self.createInstance( file_server )
    
    #//-------------------------------------------------------//
    #// modify file server
    
    new_file_server.is_nfs = 'true'
    modified_file_server = self.modifyInstance( new_file_server )
    
    #//-------------------------------------------------------//
    #// 
    if len(self.port_names) > 1:
      interface = InterfaceSettings()
      interface.id = modified_file_server.interface_ids[0]
      interface.device = self.port_names[1]
      
      if len(self.settings.interfaces) > 1:
        interface.ip = self.settings.interfaces[1]
      
      self.modifyInstance( interface )
    
    #//-------------------------------------------------------//
    #// delete file server
    
    self.deleteInstance( modified_file_server )
    self.deleteInstances( interfaces )
    
  #//=======================================================//
  
  def testNfsServer_ForErrors(self):
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    
    #//-------------------------------------------------------//
    #// Check invalid container id
    test_file_server = file_server.clone()
    test_file_server.container_id = ""
    self.createInstance( test_file_server, INVALID_PARAMETER )
    
    test_file_server.container_id = "container_invalid_id"
    self.createInstance( test_file_server, INVALID_PARAMETER )
    
    #//-------------------------------------------------------//
    #// Check invalid name
    test_file_server = file_server.clone()
    
    test_file_server.name = ""
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_INVALID_NAME_ERR )
  
    test_file_server.name = "a" * 100
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_INVALID_NAME_ERR )
    
    test_file_server.name = "@ab"
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_INVALID_NAME_ERR )
    
    test_file_server.name = "-ab"
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_INVALID_NAME_ERR )
    
    test_file_server.name = "a"*20 + ".test"
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_INVALID_NAME_ERR )
    
    new_file_server = self.createInstance( file_server )
    self.createInstance( file_server, NASSERVICES_FILESERVER_NAME_ALREADY_IN_USE_ERR )
    
    self.deleteInstance( new_file_server )
    
    #//-------------------------------------------------------//
    #// Check invalid interface
    test_file_server = file_server.clone()
    
    test_file_server.interface_ids = ['interface_invalid_id']
    self.createInstance( test_file_server, INVALID_PARAMETER )
    
    interfaces = self.createInterfaces( 2 )
    interface_ids = _getInstanceIds( interfaces )
    
    test_file_server.interface_ids = interface_ids
    
    self.createInstance( test_file_server, NASSERVICES_FILESERVER_TOO_MANY_INTERFACES_ERR )
    
    new_file_server = self.createInstance( file_server )
    
    new_file_server.interface_ids = ['interface_invalid_id']
    self.modifyInstance( new_file_server, INVALID_PARAMETER )
    
    new_file_server.interface_ids = interface_ids
    self.modifyInstance( new_file_server, NASSERVICES_FILESERVER_TOO_MANY_INTERFACES_ERR )
    
    self.deleteInstance( new_file_server )
    
    self.deleteInstances( interfaces )
    
    #//-------------------------------------------------------//
    #// Check invalid server id
    test_file_server = FileServerSettings()
    test_file_server.id = "file_server_invalid_id"
    
    self.modifyInstance( test_file_server, INVALID_PARAMETER )
    self.deleteInstance( test_file_server, INVALID_PARAMETER )
  
  #//=======================================================//
  
  def testCifsServer_1(self):
    
    #//-------------------------------------------------------//
    #// new file server
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    
    new_file_server = self.createInstance( file_server )
    
    #//-------------------------------------------------------//
    #// modify file server
    
    new_file_server.is_cifs = 'true'
    new_file_server.cifs_domain = self.settings.cifs_domain
    new_file_server.cifs_user = self.settings.cifs_admin_user
    new_file_server.cifs_password = self.settings.cifs_admin_password
    
    interfaces = self.createInterfaces( 1 )
    new_file_server.interface_ids = _getInstanceIds( interfaces )
    modified_file_server = self.modifyInstance( new_file_server )
    
    file_server = FileServerSettings()
    file_server.id = modified_file_server.id
    file_server.is_cifs = 'false'
    
    modified_file_server = self.modifyInstance( file_server )
    
    #//-------------------------------------------------------//
    #// delete file server
    
    self.deleteInstance( modified_file_server )
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testCifsServer_2(self):
    
    #//-------------------------------------------------------//
    #// new file server
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    interfaces = self.createInterfaces( 1 )
    file_server.interface_ids = _getInstanceIds( interfaces )
    
    new_file_server = self.createInstance( file_server )
    
    #//-------------------------------------------------------//
    #// modify file server
    
    new_file_server.is_cifs = 'true'
    new_file_server.cifs_domain = self.settings.cifs_domain
    new_file_server.cifs_user = self.settings.cifs_admin_user
    new_file_server.cifs_password = self.settings.cifs_admin_password
    modified_file_server = self.modifyInstance( new_file_server )
    
    #//-------------------------------------------------------//
    #// 
    if len(self.port_names) > 1:
      interface = InterfaceSettings()
      interface.id = modified_file_server.interface_ids[0]
      interface.device = self.port_names[1]
      
      if len(self.settings.interfaces) > 1:
        interface.ip = self.settings.interfaces[1]
      
      interface = self.modifyInstance( interface )
      
      interface.device = self.port_names[0]
      interface = self.modifyInstance( interface )
    
    #//-------------------------------------------------------//
    #// delete file server
    
    self.deleteInstance( modified_file_server )
    self.deleteInstances( interfaces )
    
  def testCifsServer_Restore(self):
    
    #//-------------------------------------------------------//
    #// new file server
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    interfaces = self.createInterfaces( 1 )
    file_server.interface_ids = _getInstanceIds( interfaces )
    
    new_file_server = self.createInstance( file_server )
    
    #//-------------------------------------------------------//
    #// modify file server
    
    new_file_server.is_cifs = 'true'
    new_file_server.cifs_domain = self.settings.cifs_domain
    new_file_server.cifs_user = self.settings.cifs_admin_user
    new_file_server.cifs_password = self.settings.cifs_admin_password
    modified_file_server = self.modifyInstance( new_file_server )
    
    #//-------------------------------------------------------//
    
    modified_file_server.interface_ids = []
    modified_file_server = self.modifyInstance( modified_file_server )
    self.assertEqual( modified_file_server.cifs_domain, self.settings.cifs_domain )
    
    modified_file_server.interface_ids = file_server.interface_ids
    modified_file_server = self.modifyInstance( modified_file_server )
    self.assertEqual( modified_file_server.cifs_domain, self.settings.cifs_domain )
    
    #//-------------------------------------------------------//
    
    self.deleteInstances( interfaces )
    
    modified_file_server = self.listInstances( FileServerSettings )
    self.assertEqual( len(modified_file_server), 1 )
    
    modified_file_server = modified_file_server[0]
    self.assertEqual( modified_file_server.cifs_domain, self.settings.cifs_domain )
    
    interfaces = self.createInterfaces( 1 )
    modified_file_server.interface_ids = _getInstanceIds( interfaces )
    modified_file_server = self.modifyInstance( modified_file_server )
    self.assertEqual( modified_file_server.cifs_domain, self.settings.cifs_domain )
    
    self.deleteInstance( modified_file_server )
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testCifsServer_ForErrors(self):
    
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    
    interfaces = self.createInterfaces( 1 )
    interface_ids = _getInstanceIds( interfaces )
    file_server.interface_ids = interface_ids
    
    file_server = self.createInstance( file_server )
    
    file_server.is_cifs = 'true'
    file_server.cifs_domain = self.settings.cifs_domain
    file_server.cifs_user = self.settings.cifs_admin_user
    file_server.cifs_password = self.settings.cifs_admin_password
    
    #//-------------------------------------------------------//
    #// Check invalid CIFS domain
    test_file_server = file_server.clone()
    test_file_server.cifs_domain = "test-cifs.test-sanity.emc.com"
    
    self.modifyInstance( test_file_server, [NASSERVICES_FILESERVER_NO_DC_IN_DOMAIN, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    #//-------------------------------------------------------//
    #// Check invalid CIFS user
    test_file_server = file_server.clone()
    
    test_file_server.cifs_user = ""
    self.modifyInstance( test_file_server, [NASSERVICES_FILESERVER_NO_CIFS_USER_NAME_ERR, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    test_file_server.cifs_user = "user_invalid_id"
    self.modifyInstance( test_file_server, [NASSERVICES_FILESERVER_INVALID_USER_OR_PASSWORD, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    #//-------------------------------------------------------//
    #// Check invalid CIFS password
    test_file_server = file_server.clone()
    
    test_file_server.cifs_password = ""
    self.modifyInstance( test_file_server, [NASSERVICES_FILESERVER_NO_CIFS_USER_PASSWORD_ERR, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    test_file_server.cifs_password = "invalid_password"
    self.modifyInstance( test_file_server, [ NASSERVICES_FILESERVER_INVALID_USER_OR_PASSWORD, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    #//-------------------------------------------------------//
    #// Check non-admin CIFS user
    test_file_server = file_server.clone()
    
    test_file_server.cifs_user = self.settings.cifs_nonadmin_user
    test_file_server.cifs_password = self.settings.cifs_nonadmin_password
    self.modifyInstance( test_file_server, [ NASSERVICES_FILESERVER_CANNOT_CREATE_COMPNAME_IN_AD, NASSERVICES_FILESERVER_JOIN_FAILED_ERR ] )
    
    #//-------------------------------------------------------//
    
    self.deleteInstance( file_server )
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def   _getDefaultRoute( self ):
    container_id = self.container_ids[0]
    
    routes = self.listInstances( RouteSettings )
    for route in routes:
      if (route.container_id == container_id) and (route.type == 'default'):
        return route
    
    return None
  
  #//-------------------------------------------------------//
  
  def   _createDefaultRoute( self ):
    route = self._getDefaultRoute()
    if route:
      return route
    
    route = RouteSettings()
    route.container_id = self.container_ids[0]
    route.type = 'default'
    route.gateway = self.settings.default_gateway
    
    return self.createInstance( route )
  
  #//-------------------------------------------------------//
  
  def   _deleteDefaultRoute( self ):
    
    route = self._getDefaultRoute()
    if route:
      self.deleteInstance( route )
  
  #//-------------------------------------------------------//
  
  def testRoutes(self):
    
    self._deleteDefaultRoute()
    
    container = self.container_ids[0]
    
    interfaces = self.createInterfaces( -1, create_default_gateway = False )
    self.assert_( not hasattr(interfaces[0], 'gateway') )
    
    new_route = self._createDefaultRoute()
    
    container = self.listInstances( ContainerSettings )[0]
    self.assert_( hasattr(container, 'route_ids') and (new_route.id in container.route_ids) )
    
    all_interfaces = self.listInstances( InterfaceSettings )
    self.assert_( hasattr(all_interfaces[0], 'gateway') and (all_interfaces[0].gateway == self.settings.default_gateway) )
    
    modified_route = RouteSettings()
    modified_route.id = new_route.id
    
    modified_route.destination = '192.168.0.0'
    modified_route.gateway = self.settings.default_gateway
    modified_route.netmask = '255.255.0.0'
    modified_route = self.modifyInstance( modified_route )
    
    self.deleteInstance( modified_route )
    self.deleteInstances( interfaces )
    
  def testRoutes_2(self):
    
    self._deleteDefaultRoute()
    
    interfaces = self.createInterfaces( 1, create_default_gateway = False )
    
    route = RouteSettings()
    route.container_id  = self.container_ids[0]
    route.type          = 'net'
    route.destination   = '192.168.0.0'
    route.gateway       = self.settings.default_gateway
    route.netmask       = '255.255.0.0'
    
    self.deleteInstance( self.createInstance( route ) )
    
    #//-------------------------------------------------------//
    
    route.type          = 'host'
    route.destination   = '192.168.1.1'
    del route.netmask
    
    self.deleteInstance( self.createInstance( route ) )
    
    #//-------------------------------------------------------//
    
    self.deleteInstances( interfaces )
    
  #//=======================================================//
  
  def testRoutes_Errors(self):
    
    self._deleteDefaultRoute()
    
    route = RouteSettings()
    route.container_id = self.container_ids[0]
    route.type = 'net'
    route.destination = '192.168.1.0'
    route.gateway = self.settings.default_gateway
    route.netmask = '255.255.255.0'
    
    #//-------------------------------------------------------//
    #// no interfaces yet, gateway unreachable
    
    self.createInstance( route, NASSERVICES_ROUTE_GATEWAY_UNREACHABLE_ERR )
    
    #//-------------------------------------------------------//
    interfaces = self.createInterfaces( create_default_gateway = False )
    self.deleteInstance( self.createInstance( route ) )
    
    #//-------------------------------------------------------//
    
    self.createInstance( RouteSettings(), INVALID_PARAMETER )
    
    #//-------------------------------------------------------//
    #// Check invalid container id
    
    bad_route = route.clone()
    
    del bad_route.container_id
    self.createInstance( bad_route, INVALID_PARAMETER )
    
    bad_route.container_id = ""
    self.createInstance( bad_route, INVALID_PARAMETER )
    
    bad_route.container_id = "container_invalid_id"
    self.createInstance( bad_route, INVALID_PARAMETER )
    
    #//-------------------------------------------------------//
    #// Check Type
    
    bad_route = route.clone()
    
    del bad_route.type
    self.createInstance( bad_route, NASSERVICES_ROUTE_MISSING_TYPE_ERR )
    
    bad_route.type = ""
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_TYPE_ERR )
    
    bad_route.type = "invalid_type"
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_TYPE_ERR )
    
    #//-------------------------------------------------------//
    #// Check Gateway

    bad_route = route.clone()
    
    del bad_route.gateway
    self.createInstance( bad_route, NASSERVICES_ROUTE_MISSING_GATEWAY_ERR )
    
    bad_route.gateway = ""
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_GATEWAY_ERR )
    
    bad_route.gateway = "invalid_gateway"
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_GATEWAY_ERR )
    
    bad_route.gateway = "0.0.0.0"
    self.createInstance( bad_route, NASSERVICES_ROUTE_GATEWAY_UNREACHABLE_ERR )
    
    bad_route.gateway = _incrementIP( bad_route.gateway )
    self.createInstance( bad_route, NASSERVICES_ROUTE_GATEWAY_UNREACHABLE_ERR )
    
    #//-------------------------------------------------------//
    #// Check Netmask

    bad_route = route.clone()
    
    del bad_route.netmask
    self.deleteInstance( self.createInstance( bad_route ) )   # // should be OK, using default netmask 255.255.255.0
    
    bad_route.netmask = ""
    self.createInstance( bad_route, NASSERVICES_INTERFACE_INVALID_NETMASK_ERR )
    
    bad_route.netmask = "invalid_netmask"
    self.createInstance( bad_route, NASSERVICES_INTERFACE_INVALID_NETMASK_ERR )
    
    #//-------------------------------------------------------//
    #// Check Destination

    bad_route = route.clone()
    
    del bad_route.destination
    self.createInstance( bad_route, NASSERVICES_ROUTE_MISSING_DESTINATION_ERR )
    
    bad_route.destination = ""
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_DESTINATION_ERR )
    
    bad_route.destination = "invalid_destination"
    self.createInstance( bad_route, NASSERVICES_ROUTE_INVALID_DESTINATION_ERR )
    
    #//-------------------------------------------------------//
    
    self.deleteInstances( interfaces )
  
  #//=======================================================//
  
  def testRoutes_noInterfaces(self):
    interfaces = self.createInterfaces( 1, create_default_gateway = True )
    
    default_route = RouteSettings()
    default_route.type      = 'default'
    default_route.gateway   = self.settings.default_gateway
    
    self.assertEqual( self._getDefaultRoute(), default_route )
    
    self.deleteInstances( interfaces )
    
    self.assertEqual( self._getDefaultRoute(), default_route )
  
  #//=======================================================//
  
  def test_CreateInterface(self):
    
    new_interface = self.createInterfaces( 1 )[0]
    
    self.deleteInstance( new_interface )
    
  #//=======================================================//
  
  def   createNfsServer( self, interfaces ):
    file_server = FileServerSettings()
    file_server.name = _getServerName()
    file_server.container_id = self.container_ids[0]
    file_server.interface_ids = _getInstanceIds( interfaces )
    
    file_server = self.createInstance( file_server )
    
    file_server.is_nfs = 'true'
    file_server = self.modifyInstance( file_server )
  
  #//=======================================================//
  
  def   getStorageool( self ):
    pools = self.listInstances( StoragePoolSettings )
    for pool in pools:
      if int(pool.total_capacity) > 0:
        return pool
    
    return None
  
  #//=======================================================//
  
  #~ def test_Memory_NFS_Thin(self):
    #~ interfaces = self.createInterfaces( 1 )
    #~ file_server = self.createNfsServer( interfaces )
    
    #~ pool = self.getStorageool()
    #~ if pool is not None:
      #~ pass
    
    
    #~ #//-------------------------------------------------------//
    #~ #// delete file server
    
    #~ self.deleteInstance( file_server )
    #~ self.deleteInstances( interfaces )
  #//=======================================================//
  
  def _test_DeleteServers(self):
    servers = self.listInstances( FileServerSettings )
    servers += self.listInstances( IscsiServerSettings )
    
    for server in servers:
      interface_ids = server.interface_ids
      self.deleteInstance( server )
      
      for interface_id in interface_ids:
        interface = InterfaceSettings()
        interface.id = interface_id
        self.deleteInstance( interface )
    
  #//=======================================================//
  
  def _test_DeleteInterfaces(self):
    self.deleteInstances( self.listInstances( InterfaceSettings ) )
    
  #//=======================================================//


#//===========================================================================//
#//===========================================================================//

if __name__ == "__main__":
  
  settings = _GlobalSettings()
  
  #//-------------------------------------------------------//
  
  tests = settings.tests
  
  exec_tests = set()
  append_tests = set()
  remove_tests = set()
  
  for test in tests:
    if test.startswith('+'):
      append_tests.add( test[1:] )
    
    elif test.startswith('-'):
      remove_tests.add( test[1:] )
    elif test:
      exec_tests.add( test )
  
  if not exec_tests:
    for name, instance in SanityTest.__dict__.iteritems():
      if callable(instance) and name.startswith('test'):
        exec_tests.add( name )
  
  exec_tests -= remove_tests
  exec_tests |= append_tests
  
  tests = sorted(exec_tests)
  
  #//-------------------------------------------------------//
  
  connection = _Connection( settings.cem_url, settings.cem_login, settings.cem_password, settings.verbose )
  
  port_names = _getPorts( connection )
  
  assert len(port_names) > 0

  container_ids = _getContainers( connection )
  assert len(container_ids) > 0
  
  #//-------------------------------------------------------//
  
  suite = unittest.TestSuite()
  for test_method in tests:
    suite.addTest(SanityTest( test_method, settings, connection, port_names, container_ids ))
  
  #//-------------------------------------------------------//
  
  if settings.cleanup:
    _deleteInstances( connection, FileServerSettings, IscsiServerSettings, RouteSettings, InterfaceSettings )
    
  _addDnsServer( connection, settings.cifs_domain, settings.cifs_dns )
  _addNtpServer( connection, settings )
  
  #//-------------------------------------------------------//
  
  try:
    unittest.TextTestRunner().run(suite)
  except CemError, e:
    print dir(e)
    print e

