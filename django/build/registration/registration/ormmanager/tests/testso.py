# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from registration.ormmanager.tests.somodel import User, Group
from registration.ormmanager.tests.generic import GeneralTests, set_user_class

#from sqlobject import connectionForURI, sqlhub

#connection = connectionForURI('sqlite:/:memory:')
#sqlhub.processConnection = connection


class TestSqlObject(GeneralTests):
    
    def __init__(self):
        super(TestSqlObject, self).__init__()
        set_user_class(User)
    
    def setUp(self):
        # Create tables
        User.createTable()
        Group.createTable()
        self.user1 = User(user_name='bobvilla', 
            email_address='bob@homedepot.com',
            display_name='Bob Villa',
            password='toughasnails')     
        u2 = User(user_name='bobathome',
            email_address='bob@home.com',
            display_name='Bob Villa',
            password='hammertime')
        
    def test_setup(self):
        "Ensure our setup has been processed."
        assert User.tableExists()
        u2 = User.selectBy(email_address='bob@home.com')[0]
        print u2
        assert u2.user_name=='bobathome'
        
        
    def tearDown(self):
        User.dropTable()
        Group.dropTable()