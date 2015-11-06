from ubuntu:latest

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
  Cheetah\
  Cython\
  Django\
  Django-celery\
  Django-registration-redux\
  docutils\
  Fipy\
  H5py

RUN pip install\
  libtiff\
  MySQL-python\
  networkx\
  nibabel\
  Pillow\
  posix-ipc\
  pycparser\
  Pylibmc\
  pytest\
  requests\
  Scipy\
  turbogears --allow-external PEAK-Rules --allow-unverified PEAK-Rules\
  uWSGI --allow-external PEAK-Rules --allow-unverified PEAK-Rules

RUN apt-get install -y\
  mysql-server

RUN service mysql start

RUN pip install\
  igraph\
  Registration

# make neurodata user
RUN groupadd -r neurodata && useradd -r -m -g neurodata neurodata

# make the logging directory
RUN mkdir /var/log/ocp
RUN chown neurodata:neurodata /var/log/ocp

#rest happens in user land
USER neurodata

# clone OCP
WORKDIR /home/neurodata
RUN git clone https://github.com/openconnectome/open-connectome.git

# build ocplib ctypes functions
USER root
WORKDIR /home/neurodata/open-connectome/ocplib
RUN make -f makefile_LINUX

# make cython accelerators
WORKDIR /home/neurodata/open-connectome/cython/ocpca_cy/
RUN python setup.py install

# configure mysql
WORKDIR /home/neurodata/open-connectome/django
RUN service mysql start && mysql -u root -i -e "create user 'neurodata'@'localhost' identified by 'neur0data';" &&\
  mysql -u root -i -e "grant all privileges on *.* to 'neurodata'@'localhost' with grant option;" &&\
  mysql -u neurodata -pneur0data -i -e "CREATE DATABASE ocpdjango;"

# set up the django settings
WORKDIR /home/neurodata/open-connectome/django
ADD settings.py ./OCP/settings.py
ADD settings_secret.py ./OCP/settings_secret.py
RUN service mysql start && python manage.py migrate &&\ 
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('neurodata', 'brain@brain.brain', 'neur0data')" | python manage.py shell
RUN python manage.py collectstatic --noinput



# for randal
RUN apt-get install -y openssh-server
RUN update-rc.d mysql defaults
RUN sudo update-rc.d ssh defaults
RUN echo "set -o vi" >> /etc/profile
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN passwd f00f00
