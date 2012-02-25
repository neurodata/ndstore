import web
import ocpopenid

urls = (
    r'/login/openid', 'ocpopenid.host',
    r'/login', 'Login',
)

app = web.application(urls, globals())

pagetext='''
        <html><head><title>OCP OpenID</title></head>
        <h3>Open Connectome Project: Annotation Service</h3>
        <body>
            %s
        </body>
        </html>
        '''

class Login:

  def GET(self):
    i = web.input(error=None) 
    if i.error:
      message = 'Invalid Open Id'
    else:
      message = ''
    body = pagetext % (ocpopenid.form('login/openid',message))
    return body

if __name__ == "__main__": app.run()
