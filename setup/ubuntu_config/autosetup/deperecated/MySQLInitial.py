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
import sys

# Edit the following: 
# MySQLPass - MySQL root user password
# password_here - the password for user(in this case brain) specified in the settings_secret.py file

def setup(MySQLPass, BrainPass):
	
	# Assuming ocpdjango (from settings_secret.py)

	db = MySQLdb.connect("localhost","root",MySQLPass)
	cursor = db.cursor()

	# Create database for OCP
	cursor.execute("create database ocpdjango;")

	# Create users for OCP
	cursor.execute("create user 'brain'@'localhost' identified by '" + BrainPass + "';")
	cursor.execute("grant all privileges on *.* to 'brain'@'localhost' with grant option;")

	cursor.execute("create user 'brain'@'%' identified by '" + BrainPass + "';")
	cursor.execute("grant all privileges on *.* to 'brain'@'%' with grant option;")

	db.close()

if __name__ == '__main__':
	setup(*sys.argv[1:])
