#!/bin/bash
# Installation script for ndstore backend
# Maintainer: Kunal Lillaney <lillaney@jhu.edu>
# Operating System: Ubuntu 14.04/16.04
# Usage: ./ndstore_install BRANCH PRODUCTION DOMAIN EMAIL

UBUNTU_VERSION="$(sudo lsb_release -rs)"

# update the sys packages and upgrade them
sudo apt-get update && sudo apt-get upgrade -y

# apt-get install mysql packages
echo "mysql-server mysql-server/root_password password neur0data" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password neur0data" | sudo debconf-set-selections
sudo debconf-set-selections <<< "postfix postfix/mailname string openconnecto.me"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
#sudo apt-get -y install mysql-client-core libhdf5-serial-dev mysql-client

# apt-get install packages
sudo apt-get -qq -y install nginx git bash-completion libhdf5-dev libxslt1-dev libmemcached-dev g++ libjpeg-dev virtualenvwrapper python3-dev mysql-server libmysqlclient-dev xfsprogs supervisor rabbitmq-server uwsgi uwsgi-plugin-python liblapack-dev wget memcached postfix libffi-dev libssl-dev tcl screen libhdf5-serial-dev mysql-client ruby ruby-dev

# create the log directory
sudo mkdir /var/log/neurodata
sudo touch /var/log/neurodata/ndstore.log
sudo chown -R www-data:www-data /var/log/neurodata
sudo chmod -R 777 /var/log/neurodata/

# add group and user neurodata
sudo addgroup neurodata
sudo useradd -m -p neur0data -g neurodata -s /bin/bash neurodata

# add group and user redis
sudo addgroup redis
sudo useradd -M --system -g redis redis

# switch user to neurodata and clone the repo with sub-modules
cd /home/neurodata
sudo -u neurodata git clone https://github.com/neurodata/ndstore -q
cd /home/neurodata/ndstore
if [ -z "$1" ]; then
  sudo -u neurodata git checkout microns -q
else
  sudo -u neurodata git checkout "$1" -q
fi
sudo -u neurodata git submodule init
sudo -u neurodata git submodule update

# pip install packages
cd /home/neurodata/ndstore/setup/
# temp patch to install pip on 14.04 broken because of old python version supposedly not safe
sudo wget https://bootstrap.pypa.io/get-pip.py .
sudo python3 get-pip.py
sudo -H pip install -U cython numpy
sudo -H pip install -U -r requirements.txt

# switch user to neurodata and make ctypes functions
cd /home/neurodata/ndstore/ndlib/c_version
sudo -u neurodata make -f makefile_LINUX

# configure mysql
cd /home/neurodata/ndstore/django/
sudo service mysql start
mysql -u root -pneur0data -i -e "create user 'neurodata'@'localhost' identified by 'neur0data';"
mysql -u root -pneur0data -i -e "grant all privileges on *.* to 'neurodata'@'localhost' with grant option;"
mysql -u neurodata -pneur0data -i -e "CREATE DATABASE neurodjango;"

# configure django setttings
cd /home/neurodata/ndstore/django/ND/
sudo -u neurodata cp settings.py.example settings.py
sudo -u neurodata ln -s /home/neurodata/ndstore/setup/docker_config/django/docker_settings_secret.py settings_secret.py

# download, install and configure redis
cd /home/neurodata/
sudo -u neurodata wget http://download.redis.io/redis-stable.tar.gz
sudo -u neurodata tar -xvf /home/neurodata/redis-stable.tar.gz
cd /home/neurodata/redis-stable/
sudo -u neurodata make && sudo -u neurodata make test && sudo make install
sudo mkdir /etc/redis
sudo ln -s /home/neurodata/ndstore/setup/docker_config/redis/redis.conf /etc/redis/redis.conf
if [[ $UBUNTU_VERSION == "16.04" ]]; then
  sudo ln -s /home/neurodata/ndstore/setup/docker_config/systemd/redis.service /etc/systemd/system/redis.service
  # restart redis service
  sudo systemctl daemon-reload
  sudo systemctl enable redis.service
  sudo systemctl service redis restart
else
  if [[ $UBUNTU_VERSION == "14.04" ]]; then
  sudo ln -s /home/neurodata/ndstore/setup/docker_config/upstart/redis.conf /etc/init.d/system/redis.conf
  # restart redis service
  sudo service redis restart
  fi
fi 

# setup the ndingest settings file
sudo cp /home/neurodata/ndstore/ndingest/settings/settings.ini.example /home/neurodata/ndstore/ndingest/settings/settings.ini

# migrate the database and create the superuser
sudo chmod -R 777 /var/log/neurodata/
cd /home/neurodata/ndstore/django/
sudo -u neurodata python3 manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('neurodata', 'abc@xyz.com', 'neur0data')" | python3 manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_user('test', 'abc@xyz.com', 't3st')" | python3 manage.py shell
sudo -u neurodata python3 manage.py collectstatic --noinput

# add openconnecto.me to django_sites
if [ -z "$2" ]; then
  mysql -u neurodata -pneur0data -i -e "use neurodjango; insert into django_site (id, domain, name) values (2, 'openconnecto.me', 'openconnecto.me');"
else
  if [ "$2" == "PRODUCTION" ]; then
    mysql -u neurodata -pneur0data -i -e "use neurodjango; insert into django_site (id, domain, name) values (2, '$3', '$3');"
  fi
fi

# setup the cache manager
sudo ln -s /home/neurodata/ndstore/setup/docker_config/systemd/ndmanager.conf /etc/systemd/systems/ndmanager.conf
sudo systemctl daemon-reload
sudo systemctl enable ndmanager.service


# move the nginx config files and start service
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/neurodata/ndstore/setup/docker_config/nginx/ndstore.conf /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/nginx.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/nginx/nginx.conf /etc/nginx/nginx.conf

# move uwsgi config files and start service
sudo rm /etc/uwsgi/apps-available/ndstore.ini
sudo ln -s /home/neurodata/ndstore/setup/docker_config/uwsgi/ndstore.ini /etc/uwsgi/apps-available/
sudo rm /etc/uwsgi/apps-enabled/ndstore.ini
sudo ln -s /home/neurodata/ndstore/setup/docker_config/uwsgi/ndstore.ini /etc/uwsgi/apps-enabled/

# move celery config files and start service
sudo rm /etc/supervisor/conf.d/propagate.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/celery/propagate.conf /etc/supervisor/conf.d/propagate.conf
sudo rm /etc/supervisor/conf.d/ingest.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/celery/ingest.conf /etc/supervisor/conf.d/ingest.conf
sudo rm /etc/supervisor/conf.d/stats.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/celery/stats.conf /etc/supervisor/conf.d/stats.conf

sudo rm /home/neurodata/ndstore/ndingest/settings/settings.ini
sudo ln -s /home/neurodata/ndstore/ndingest/settings/settings.ini.example /home/neurodata/ndstore/ndingest/settings/settings.ini

# add ssl keys and certificates for https
if [ -z "$2" ]; then
  sudo mkdir /etc/nginx/ssl
  cd /home/neurodata/ndstore/setup/
  sudo openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/neurodata.io.key -config ssl_config.txt
  sudo openssl req -key /etc/nginx/ssl/neurodata.io.key -new -x509 -out /etc/nginx/ssl/neurodata.io.crt -config ssl_config.txt
else
  if [ "$2" == "PRODUCTION" ]; then
    sudo mkdir /etc/nginx/ssl
    cd
    wget https://dl.eff.org/certbot-auto
    chmod a+x certbot-auto
    echo "y" | sudo ./certbot-auto
    sudo ./certbot-auto certonly --noninteractive --agree-tos --email $4 --webroot -w /usr/share/nginx/html/ -d $3
    sudo cp /etc/letsencrypt/live/$3/privkey.pem /etc/nginx/ssl/neurodata.io.key
    sudo cp /etc/letsencrypt/live/$3/cert.pem /etc/nginx/ssl/neurodata.io.crt
    sudo ./certbot-auto renew --quiet --no-self-upgrade
  fi
fi

# reload all init configurations
sudo systemctl daemon-reload
# starting all the services
sudo systemctl restart redis
sudo service restart ndmanager
sudo systemctl restart nginx
sudo systemctl restart uwsgi
sudo systemctl restart supervisor
sudo systemctl restart rabbitmq-server
sudo systemctl restart memcached

# Create superuser token
cd /home/neurodata/ndstore/django/
echo "from rest_framework.authtoken.models import Token; from django.contrib.auth.models import User; u = User.objects.get(username='neurodata'); token = Token.objects.create(user=u); f = open('/tmp/token_super','wb'); f.write(token.key); f.close()" | python3 manage.py shell

cd /home/neurodata/ndstore/django/
echo "from rest_framework.authtoken.models import Token; from django.contrib.auth.models import User; u = User.objects.get(username='test'); token = Token.objects.create(user=u); f = open('/tmp/token_user','wb'); f.write(token.key); f.close()" | python3 manage.py shell

# running tests
cd /home/neurodata/ndstore/test/
if [[ -z "$TRAVIS_BRANCH" ]]; then
  py.test
fi
if [ "$?" != "0" ]; then
  cat /var/log/neurodata/ndstore.log
  exit 1
fi
