#!/bin/bash
# -m MySQLPass and -b BrainPass

MySQLPass=
BrainPass=

while getopts “:m:b:” OPTION
do
     case $OPTION in
         m)
             MySQLPass=$OPTARG
             ;;
         b)
             BrainPass=$OPTARG
             ;;
         ?)
             echo -n "Must enter passwords for MySQL server and brain user with arguements -m MySQLPass and -b BrainPass"
             exit 1
             ;;
     esac
done

if [[ -z $MySQLPass ]] || [[ -z $BrainPass ]]
then
     echo -n "Must enter passwords for MySQL server and brain user with arguements -m MySQLPass and -b BrainPass"
     exit 1
fi

# Install basic pacakges
echo -n "Install script should be placed in the open-connectome folder. "

./SudoInstalls.sh $MySQLPass $BrainPass

# Setup and install packages to the virtual enviroment
virtualenv ../OCPServer
source ../OCPServer/bin/activate
pip install setuptools
pip install numpy
pip install Scipy
pip install ez_setup
pip install Fipy
pip install Django
pip install Django-registration
pip install Django-celery
pip install MySQL-python
pip install turbogears --allow-external PEAK-Rules --allow-unverified PEAK-Rules
pip install Django-registration-redux
pip install Cython
pip install H5py
pip install Pillow
pip install Cheetah
pip install Registration
pip install Pylibmc
pip install uWSGI --allow-external PEAK-Rules --allow-unverified PEAK-Rules
pip install igraph
pip install pytest
pip install networkx
pip install docutils
pip install posix-ipc
pip install pycparser
pip install libtiff


# Setup the files needed for first run of the server

cp django/OCP/settings_secret.py.example django/OCP/settings_secret.py


if [[ "$OSTYPE" == "linux-gnu" ]]; then
        cp ocplib/makefile_LINUX ocplib/makefile
	make -C ocplib/
elif [[ "$OSTYPE" == "darwin"* ]]; then
        cp ocplib/makefile_MAC ocplib/makefile
	make -C ocplib/
else
        # Not supported.
	echo -n "Unsupported Type"
fi

# Edit values in settings_secret.py and settings.py, including location of static files? secret key, user, pass


# Set up Mysql server values
python MySQLInitial.py $MySQLPass $BrainPass

echo -n "Remember to edit the settings.py and settings_secret.py files in django/OCP before running the server using the virtual enviroment."
