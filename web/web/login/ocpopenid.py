"""ocpopenid.py: Reimplementation of (webopenid.py: an openid library for web.py)

The goal of this module is to create a token for identifying
an annotator to the OCP annotation service.  Some comments:

  An annotation database is associated with an 
    OpenID, dataset name (e.g. hayworth5nm), and resolution.

  This page will create a token, store it in the database, and
    return it to the annotator.  The annotator will use this
    token in subsequent interactions with this token.

  Running this script again replaces the previous token 
    with the new token.

  TODO : 
    (1) make OpenID stateless, 
    (3) interact with users databsae
    (4) no cookies
    (5) change logout to return
    (6) make button to write ??
   
"""

import os
import random
import hmac
import web
import openid.consumer.consumer
import openid.store.memstore

sessions = {}
store = openid.store.memstore.MemoryStore()

# RBTODO don't like the secret file.  Move to the database?
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
    print oid
    if oid:
        return '''
        Your new annotation token for database <strong> %s </strong> 
        at resolution <strong> %s </strong> is: 
        <p>
        <strong> %s </strong> 
        <p>
        Logout to leave this page.
        <form method="post" action="%s">
          <img src="http://openid.net/login-bg.gif" alt="OpenID" />
          <strong>%s</strong>
          <input type="hidden" name="action" value="logout" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log out</button>
        </form>''' % ("hayworth5nm","3","foo",openid_loc, oid, web.ctx.fullpath)
    else:
        return '''
        To reset your annotation token, specify the dataset and resolution that your
        project is annotating and put an OpenID in the OpenID box.  Login will
        redirect you to an OpenID provider.  After authenticating, your token will be
        reset and will be redirected to a page that shows you the new annotation token.
        <p>
        <form method="post" action="%s">
          <input type="text" name="openid" value="" 
            style="background: url(http://openid.net/login-bg.gif) no-repeat; padding-left: 18px; background-position: 0 50%%;" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log in</button>
          <p>
          <strong> %s </strong>
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
