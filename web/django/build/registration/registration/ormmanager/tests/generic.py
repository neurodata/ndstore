from registration import ormmanager

User = None

class GeneralTests(object):
    
    def __init__(self):
        super(GeneralTests, self).__init__()
        self.user1 = None
    
    def test_create(self):
        "Create a new object."
        u = ormmanager.create(User, user_name='bobevans', 
                   email_address='bob@example.com', 
                   display_name='Bob Evans',
                   password='secretsauce')
        assert u.user_name=='bobevans'
        assert u.id > 0
       
    def test_retrieve_singleKW(self):
        "retrieve works with a single keyword"
        u = ormmanager.retrieve(User, user_name='bobvilla')
        assert len(u) == 1, u
        assert u[0].password == 'toughasnails'
            
    def test_retrieve_multipleKW(self):
        "retrieve works with multiple keywords"
        u = ormmanager.retrieve(User, user_name='bobvilla', 
                           email_address='bob@homedepot.com')
        assert len(u) == 1, u
        assert u[0].password == 'toughasnails'
       
    def test_retrieve_noKW(self):
        "retreive works with no keywords"
        u = ormmanager.retrieve(User)
        assert len(u) == 2
        for user in u:
            assert user.display_name=='Bob Villa', (user, user.display_name)
            assert user.user_name[:3] == 'bob'
   
    def test_retrieve_multipleObjs(self):
        "Multiple objects can be retrieved using keywords."
        u = ormmanager.retrieve(User, display_name='Bob Villa')
        assert len(u) == 2
        for user in u:
            assert user.display_name=='Bob Villa', user.display_name
            assert user.user_name[:3] == 'bob'
           
    def test_retrieve_empty(self):
        "retrieve returns an empty list when no matches are found"
        u = ormmanager.retrieve(User, user_name='bobdog')
        assert u == []
       
    def test_retrieve_one_singleKW(self):
        "retrieve_one works with a single keyword."
        u = ormmanager.retrieve_one(User, user_name='bobvilla')
        assert isinstance(u, User)
        assert u.password == 'toughasnails'
        
    def test_retrieve_one_multipleKW(self):
        "retrieve_one works with multiple keywords"
        u = ormmanager.retrieve_one(User, user_name='bobvilla', 
                           email_address='bob@homedepot.com')
        assert isinstance(u, User)
        assert u.password == 'toughasnails'
       
    def test_retrieve_one_returnNone(self):
        "retrieve_one returns None when no matches are found"
        u = ormmanager.retrieve_one(User, user_name='bobdog')
        assert u is None
       
    def test_retrieve_one_raiseError(self):
        "An exeption is raised when multiple objects are found."
        gotError = False
        try:
            u = ormmanager.retrieve_one(User, display_name='Bob Villa')
        except LookupError:
            gotError = True
        assert gotError
        
    def test_update_singleKW(self):
        "update works with a single keyword"
        u = self.user1
        ormmanager.update(u, password='ihearttools')
        assert u.user_name=='bobvilla'
        assert u.password=='ihearttools'

    def test_update_multipleKW(self):
        "update works with multiple keywords"
        u = self.user1
        ormmanager.update(u, password='ihearttools', email_address='bob@example.com')
        assert u.user_name=='bobvilla', str(u.user_name)
        assert u.password=='ihearttools'
        assert u.email_address=='bob@example.com'
       
    def test_delete(self):
        "delete an object from the database"
        u = ormmanager.retrieve_one(User, user_name='bobvilla')
        ormmanager.delete(u)
        assert ormmanager.retrieve_one(User, user_name='bobvilla') is None
       
    def test_count_noKW(self):
        "Count given no keywords"
        count = ormmanager.count(User)
        assert count == 2
       
    def test_count_KW(self):
        "Count given keywords"
        count = ormmanager.count(User, user_name='bobvilla')
        assert count == 1 
       
def set_user_class(class_):
    global User
    User = class_
       
