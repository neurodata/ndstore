#!/bin/bash

MySQLPass=$1
BrainPass=$2

if [ $EUID != 0 ]; then
	sudo "$0" "$@"
	exit $?
fi

# Install basic pacakges
echo -n "Install script should be placed in the open-connectome folder. "

debconf-set-selections <<< 'mysql-server mysql-server/root_password password '$MySQLPass
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password '$MySQLPass
apt-get -y install mysql-server

apt-get -y install Python-pip python-mysqldb libmysqld-dev python-dev liblapack-dev gfortran libmemcached-dev Libhdf5-dev python-pytest python-virtualenv

mkdir /var/log/ocp
chown www-data:www-data /var/log/ocp
touch /var/log/ocp/ocp.log
chmod 777 /var/log/ocp/ocp.log





