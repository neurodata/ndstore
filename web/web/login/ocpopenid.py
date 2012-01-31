"""ocpopenid.py: Reimplementation of (openid.py: an openid library for web.py)

Notes:

 - This will create a file called .openid_secret_key in the 
   current directory with your secret key in it. If someone 
   has access to this file they can log in as any user. And 
   if the app can't find this file for any reason (e.g. you 
   moved the app somewhere else) then each currently logged 
   in user will get logged out.

 - State must be maintained through the entire auth process 
   -- this means that if you have multiple web.py processes 
   serving one set of URLs or if you restart your app often 
   then log ins will fail. You have to replace sessions and 
   store for things to work.

 - We set cookies starting with "openid_".

"""

import os
import random
import hmac
import web
import openid.consumer.consumer
import openid.store.memstore

sessions = {}
store = openid.store.memstore.MemoryStore()

def _secret():
    try:
        secret = file('.openid_secret_key').read()
    except IOError:
        # file doesn't exist
        secret = os.urandom(20)
        file('.openid_secret_key', 'w').write(secret)
    return secret

def _hmac(identity_url):
    return hmac.new(_secret(), identity_url).hexdigest()

def _random_session():
    n = random.random()
    while n in sessions:
        n = random.random()
    n = str(n)
    return n

def status():
    oid_hash = web.cookies().get('openid_identity_hash', '').split(',', 1)
    if len(oid_hash) > 1:
        oid_hash, identity_url = oid_hash
        if oid_hash == _hmac(identity_url):
            return identity_url
    return None

def form(openid_loc,message):
    oid = status()
    if oid:
        return '''
        <form method="post" action="%s">
          <img src="http://openid.net/login-bg.gif" alt="OpenID" />
          <strong>%s</strong>
          <input type="hidden" name="action" value="logout" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log out</button>
        </form>''' % (openid_loc, oid, web.ctx.fullpath)
    else:
        return '''
        <form method="post" action="%s">
          <input type="text" name="openid" value="" 
            style="background: url(http://openid.net/login-bg.gif) no-repeat; padding-left: 18px; background-position: 0 50%%;" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log in</button>
          <p>
          Message = %s
          </p>
        </form>''' % (openid_loc, web.ctx.fullpath, message)

def logout():
    web.setcookie('openid_identity_hash', '', expires=-1)

class host:
    def POST(self):
        # unlike the usual scheme of things, the POST is actually called
        # first here
        i = web.input(return_to='/')
        if i.get('action') == 'logout':
            logout()
            return web.seeother(i.return_to)

        i = web.input('openid', return_to='/')

        #Remove the arguments
        return_to = i.return_to.partition('?')[0]

        n = _random_session()
        sessions[n] = {'webpy_return_to': return_to}
        
        c = openid.consumer.consumer.Consumer(sessions[n], store)
        try:
          a = c.begin(i.openid)
        except:
          return web.seeother(return_to + '?error=1') 

        f = a.redirectURL(web.ctx.home, web.ctx.home + web.ctx.fullpath)

        web.setcookie('openid_session_id', n)
        return web.seeother(f)

    def GET(self):
        n = web.cookies('openid_session_id').openid_session_id
        web.setcookie('openid_session_id', '', expires=-1)
        return_to = sessions[n]['webpy_return_to']

        c = openid.consumer.consumer.Consumer(sessions[n], store)
        a = c.complete(web.input(), web.ctx.home + web.ctx.fullpath)

        if a.status.lower() == 'success':
            web.setcookie('openid_identity_hash', _hmac(a.identity_url) + ',' + a.identity_url)

        del sessions[n]
        return web.seeother(return_to)
