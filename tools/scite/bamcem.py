#!/usr/bin/python

import urllib2
import xml.parsers.expat

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

def   _sendRequest( ip, data, verbose, session_id = "" ):
  global _NEXT_TASK_ID
  global _CURRENT_TASK_ID
  
  req = urllib2.Request( "https://%s/cemUI.html" % ip )
  
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

def   _getSessionId( ip, login, password, verbose ):
  
  global _NEXT_TASK_ID
  global _CURRENT_TASK_ID
  
  data = '<Login>' + \
              '<Users>' + \
                '<User requestId="%s" name="%s" password="%s" authenticationType="basic" hostIp="1.1.1.1"/>' % (_NEXT_TASK_ID, login, password) + \
              '</Users>' + \
            '</Login>'
  
  http_response = _sendRequest( ip, data, verbose )
  
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

class Connection( object ):
  __slots__ = ( 'handle', 'ip', 'session_id' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, ip, login, password, verbose = True ):
    session_id = _getSessionId( ip, login, password, verbose )
    
    handle = _sendRequest( ip, '<Connect><CemSystem/></Connect>', verbose, session_id )
    
    while True:
      xml_node = _readXmlResponse( handle, verbose )
      if xml_node is not None:
        node = xml_node.find( 'bam:SessionConnected' )
        if (node is not None) and (node.attrs.get('sessionId', '0') == session_id ):
          break
    
    self.handle = handle
    self.ip = ip
    self.session_id = session_id
  
  #//-------------------------------------------------------//
  
  def   send( self, request, verbose = True):
    return _sendRequest( self.ip, request, verbose, self.session_id )
  
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

#//=======================================================//

def   sendRequest( ip, login, password, request, verbose, keep ):
  
  connection = Connection( ip, login, password, verbose )
  
  if request is not None:
    connection.send( request, verbose )
    xml_node = connection.recv( verbose )
    if not verbose:
      print "\n\nResponse:\n", xml_node.text
  
  if keep and verbose:
    while True:
      xml_node = connection.read( verbose )
      if xml_node is None:
        break
  
  connection.close()

#//=======================================================//

if __name__ == "__main__":
  
  from optparse import OptionParser
  
  parser = OptionParser()
  parser.add_option("-i", "--host", dest="host",
                    help = "IP address or name of CEM", metavar = "HOST")
  
  parser.add_option("-u", "--user", dest="user",
                    default="Local/admin",
                    help = "User's login", metavar = "USER")
  
  parser.add_option("-p", "--password", dest = "password",
                    default="Password123!",
                    help = "User's password", metavar = "PASSWORD")
  
  parser.add_option("-r", "--request", dest = "request",
                    help = "BAM XML request", metavar = "BAM_XML_REQUEST")
  
  parser.add_option("-f", "--file", dest = "request_file",
                    help = "BAM XML request file", metavar = "BAM_XML_REQUEST_FILE")
  
  parser.add_option("-v", action="store_true", dest="verbose",
                     help = "Verbose mode", default = True )
  
  parser.add_option("-q", action="store_false", dest="verbose",
                    help = "Quiet mode", default = True )
  
  parser.add_option("-k", "--keep", action="store_true", dest="keep",
                    help = "Don't close connection upon response", default = False )
  
  (options, args) = parser.parse_args()
  
  print_usage = False
  
  if options.host is None:
    print "Error: CEM host is not specified"
    print_usage = True
  
  elif options.user is None:
    print "Error: User's login is not specified"
    print_usage = True
  
  elif options.password is None:
    print "Error: User's login is not specified"
    print_usage = True
  
  request = None
  
  if options.request is not None:
    request = options.request
  elif options.request_file is not None:
    request = ''.join( open(options.request_file).readlines() )
    
  if print_usage:
    parser.print_help()
  else:
    if request is not None:
      _verifyXml( request )
    
    sendRequest( options.host, options.user, options.password, request, options.verbose, options.keep )

