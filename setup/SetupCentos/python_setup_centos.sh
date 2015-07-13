#!/bin/bash

# Install required packagess
yum -y update
yum -y groupinstall "Development tools"
yum -y install zlib-devel  bzip2-devel openssl-devel ncurses-devel mysql-devel libxml2-devel libxslt-devel unixODBC-devel sqlite sqlite-devel xz-libs

# Install Python 2.7.9 (do NOT remove 2.6, by the way)
wget --no-check-certificate http://www.python.org/ftp/python/2.7.9/Python-2.7.9.tar.xz
xz -d Python-2.7.9.tar.xz
tar -xvf Python-2.7.9.tar 
cd Python-2.7.9
./configure --prefix=/usr/local 
make 
make altinstall

# Install setuptools and env
wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py
python2.7 ez-setup.py --insecure

#wget httpe://boostrap.pypa.io/ez_setup.py -O | python2.7
curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python2.7 -

pip install virtualenv

# Now you can do: `mkvirtualenv foo --python=python2.7`
