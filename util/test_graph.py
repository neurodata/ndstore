import urllib2

token = 'test_token'
channel = 'test_channel'
graphtype = 'test'

url = 'http://{}/ocpgraph/{}/{}/{}/'.format('localhost:8000', token, channel, graphtype)
try:
  req = urllib2.Request(url)
  resposne = urllib2.urlopen(req)
except Exception, e:
  raise
