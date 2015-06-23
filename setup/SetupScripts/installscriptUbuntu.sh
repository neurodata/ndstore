#!/bin/bash
echo -n "Install script should be placed in the open-connectome folder. "
sudo apt-get install Python-pip mysql-server python-mysqldb libmysqld-dev python-dev liblapack-dev gfortran libmemcached-dev Libhdf5-dev python-pytest

echo -n "Do you wish to create a virtual enviroment (Named OCPServer) in the /home directory (y/n)? please edit the location if you wish it to be in the /home/user directory" 
read answerenv

if echo "$answerenv" | grep -iq "^y" ;then
	sudo apt-get install python-virtualenv
#CAN EDIT	
	sudo virtualenv /home/OCPServer
	source OCPServer/bin/activate
#DO NOT EDIT
else
    	echo -n "Please note it is easier to install django and other packages in a virtual enviroment."
fi


echo -n "Do you wish to install the python packages through pip (y/n)?" 
read answer
if echo "$answer" | grep -iq "^y" ;then
	source OCPServer/bin/activate
    	pip install numpy Scipy ez_setup Fipy Django Django-registration Django-celery MySQL-python TurboGears Django-registration-redux Cython H5py Pillow Cheetah Registration Pylibmc uWSGI

else
    	echo -n "Please add the packages later manually."
fi



