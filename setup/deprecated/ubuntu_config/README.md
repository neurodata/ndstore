Configuration information for nginx

** default

   OCP configuration for /etc/nginx/sites-enabled/default

** ocp.ini

  uWSGI configuration file in /etc/uwsgi/vassals/
  uWSGI configuration file in /etc/uwsgi/apps-enabled/

** packages -- to install nginx on ubuntu

Commands to restart services

  sudo /etc/init.d/uwsgi restart ocp
  sudo /etc/init.d/nginx restart
