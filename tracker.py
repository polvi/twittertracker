#!/usr/bin/python

from twisted.web.client import HTTPClientFactory
from twisted.web.http import HTTPClient
from twisted.internet import reactor

import simplejson

import sys
import base64

from secret import CREDS

CREDS=base64.b64encode(CREDS)

TRACK=sys.argv[1]

class TwitterHTTPClient(HTTPClient):

  def connectionMade(self):
    method = self.factory.method
    self.sendCommand(method, self.factory.path)
    self.sendHeader('Host', self.factory.headers.get("host", self.factory.host))
    self.sendHeader('User-Agent', self.factory.agent)
    self.sendHeader('Authorization', 'Basic %s' % (CREDS))
    self.sendHeader('Content-Type', 'application/x-www-form-urlencoded')
    data = getattr(self.factory, 'postdata', None)
    if data is not None:
      self.sendHeader("Content-Length", str(len(data)))
    self.endHeaders()
    self.headers = {}
    
    if data is not None:
      self.transport.write(data)

  def handleResponse(self, data):
    pass

  def rawDataReceived(self, data):
    try:
      res =  simplejson.loads(data)
      tweet = res['text']
      user = res['user']['name']
      print '%s: %s' % (user, tweet)
    except Exception, e:
      pass
  
class TwitterHTTPClientFactory(HTTPClientFactory):
  protocol = TwitterHTTPClient

h = TwitterHTTPClientFactory('http://stream.twitter.com/track.json', method='POST', postdata='track=%s' % (TRACK))
conn = reactor.connectTCP('stream.twitter.com', 80, h)
reactor.run()
