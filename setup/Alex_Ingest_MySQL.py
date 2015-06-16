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

import MySQLdb

#Initial definitions (change depending on database migrating)
Project_Name = "kat11segments"
Channel_Name = "kat11segments"

#Open connection and create cursor
db = MySQLdb.connect("localhost","brain","88brain88",Project_Name)
cursor = db.cursor()

#Drop old tables
cursor.execute("drop table %s" % (Channel_Name + "_annotations;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc0;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc1;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc2;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc3;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc4;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc5;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc6;"))
cursor.execute("drop table %s" % (Channel_Name + "_exc7;"))
cursor.execute("drop table %s" % (Channel_Name + "_ids;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx0;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx1;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx2;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx3;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx4;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx5;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx6;"))
cursor.execute("drop table %s" % (Channel_Name + "_idx7;"))
cursor.execute("drop table %s" % (Channel_Name + "_kvpairs;"))
cursor.execute("drop table %s" % (Channel_Name + "_organelles;"))
cursor.execute("drop table %s" % (Channel_Name + "_res0;"))
cursor.execute("drop table %s" % (Channel_Name + "_res1;"))
cursor.execute("drop table %s" % (Channel_Name + "_res2;"))
cursor.execute("drop table %s" % (Channel_Name + "_res3;"))
cursor.execute("drop table %s" % (Channel_Name + "_res4;"))
cursor.execute("drop table %s" % (Channel_Name + "_res5;"))
cursor.execute("drop table %s" % (Channel_Name + "_res6;"))
cursor.execute("drop table %s" % (Channel_Name + "_res7;"))
cursor.execute("drop table %s" % (Channel_Name + "_seeds;"))
cursor.execute("drop table %s" % (Channel_Name + "_segments;"))
cursor.execute("drop table %s" % (Channel_Name + "_synapses;"))


#Rename tables in database
cursor.execute("rename table annotations to %s" % (Channel_Name + "_annotations;"))
cursor.execute("rename table exc0 to %s" % (Channel_Name + "_exc0;"))
cursor.execute("rename table exc1 to %s" % (Channel_Name + "_exc1;"))
cursor.execute("rename table exc2 to %s" % (Channel_Name + "_exc2;"))
cursor.execute("rename table exc3 to %s" % (Channel_Name + "_exc3;"))
cursor.execute("rename table exc4 to %s" % (Channel_Name + "_exc4;"))
cursor.execute("rename table exc5 to %s" % (Channel_Name + "_exc5;"))
cursor.execute("rename table exc6 to %s" % (Channel_Name + "_exc6;"))
cursor.execute("rename table exc7 to %s" % (Channel_Name + "_exc7;"))
cursor.execute("rename table ids to %s" % (Channel_Name + "_ids;"))
cursor.execute("rename table idx0 to %s" % (Channel_Name + "_idx0;"))
cursor.execute("rename table idx1 to %s" % (Channel_Name + "_idx1;"))
cursor.execute("rename table idx2 to %s" % (Channel_Name + "_idx2;"))
cursor.execute("rename table idx3 to %s" % (Channel_Name + "_idx3;"))
cursor.execute("rename table idx4 to %s" % (Channel_Name + "_idx4;"))
cursor.execute("rename table idx5 to %s" % (Channel_Name + "_idx5;"))
cursor.execute("rename table idx6 to %s" % (Channel_Name + "_idx6;"))
cursor.execute("rename table idx7 to %s" % (Channel_Name + "_idx7;"))
cursor.execute("rename table kvpairs to %s" % (Channel_Name + "_kvpairs;"))
cursor.execute("rename table organelles to %s" % (Channel_Name + "_organelles;"))
cursor.execute("rename table res0 to %s" % (Channel_Name + "_res0;"))
cursor.execute("rename table res1 to %s" % (Channel_Name + "_res1;"))
cursor.execute("rename table res2 to %s" % (Channel_Name + "_res2;"))
cursor.execute("rename table res3 to %s" % (Channel_Name + "_res3;"))
cursor.execute("rename table res4 to %s" % (Channel_Name + "_res4;"))
cursor.execute("rename table res5 to %s" % (Channel_Name + "_res5;"))
cursor.execute("rename table res6 to %s" % (Channel_Name + "_res6;"))
cursor.execute("rename table res7 to %s" % (Channel_Name + "_res7;"))
cursor.execute("rename table seeds to %s" % (Channel_Name + "_seeds;"))
cursor.execute("rename table segments to %s" % (Channel_Name + "_segments;"))
cursor.execute("rename table synapses to %s" % (Channel_Name + "_synapses;"))

#Disconnect safely
db.close()

