from ubuntu:14.04

RUN apt-get update
RUN apt-get -y install \
  gcc\
  gfortran\
  git\
  g++\
  libatlas-dev\
  libblas-dev\
  libevent-dev\
  libhdf5-serial-dev\
  liblapack-dev\
  libmemcached-dev\
  libmysqlclient-dev\
  libxml2-dev\ 
  libxslt1-dev\
  memcached\
  nginx\
  python-all-dev\
  python-mysqldb\
  python-pip\
  wget

RUN pip install\
  ez_setup\
  numpy\
  setuptools

RUN pip install\
  blosc\
  boto3\
  Cheetah\
  Cython\
  Django==1.8\
  Django-celery\
  Django-registration-redux\
  docutils\
  Fipy\
  H5py

RUN pip install\
  libtiff\
  lxml\
  MySQL-python\
  networkx\
  nibabel\
  Pillow\
  posix-ipc\
  pycparser\
  Pylibmc\
  pytest\
  requests\
  Scipy


WORKDIR /tmp
# add PEAK-Rules needed externallly
RUN wget http://www.turbogears.org/2.0/downloads/current/PEAK-Rules-0.5a1.dev-r2686.tar.gz && tar -xvzf PEAK-Rules-0.5a1.dev-r2686.tar.gz && rm PEAK-Rules-0.5a1.dev-r2686.tar.gz
WORKDIR /tmp/PEAK-Rules-0.5a1.dev-r2686
RUN python setup.py install

RUN pip install\
  igraph\
  turbogears --allow-external PEAK-Rules --allow-unverified PEAK-Rules\
  uWSGI --allow-external PEAK-Rules --allow-unverified PEAK-Rules

RUN apt-get install -y\
  mysql-server

RUN service mysql start

# make neurodata user
RUN groupadd -r neurodata && useradd -r -m -g neurodata neurodata

# make the logging directory
RUN mkdir /var/log/ocp
RUN chown neurodata:neurodata /var/log/ocp

#rest happens in user land
USER neurodata

# add github ssh key to known hosts
RUN mkdir ~/.ssh
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# clone OCP
WORKDIR /home/neurodata
RUN git clone https://github.com/neurodata/ndstore.git
WORKDIR /home/neurodata/ndstore
RUN git checkout microns
RUN git submodule init
RUN git submodule update

## build ocplib ctypes functions
USER root
WORKDIR /home/neurodata/ndstore/ndlib/c_version
RUN make -f makefile_LINUX

# make cython accelerators
WORKDIR /home/neurodata/ndstore/cython/ocpca_cy/
RUN python setup.py install

# configure mysql
WORKDIR /home/neurodata/ndstore/django
RUN service mysql start && mysql -u root -i -e "create user 'neurodata'@'localhost' identified by 'neur0data';" &&\
  mysql -u root -i -e "grant all privileges on *.* to 'neurodata'@'localhost' with grant option;" &&\
  mysql -u neurodata -pneur0data -i -e "CREATE DATABASE ocpdjango;"

USER neurodata
# set up the django settings
#WORKDIR /home/neurodata/ndstore/django
#ADD settings.py ./OCP/settings.py
#ADD settings_secret.py ./OCP/settings_secret.py
#RUN service mysql start && python manage.py migrate &&\ 
#  echo "from django.contrib.auth.models import User; User.objects.create_superuser('neurodata', 'brain@brain.brain', 'neur0data')" | python manage.py shell
#RUN python manage.py collectstatic --noinput
#
# for randal
#RUN apt-get install -y openssh-server
#RUN update-rc.d mysql defaults
#RUN sudo update-rc.d ssh defaults
#RUN echo "set -o vi" >> /etc/profile
#RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
######RUN passwd f00f00
