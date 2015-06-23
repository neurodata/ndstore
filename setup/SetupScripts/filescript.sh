#!/bin/bash
echo -n "Are you on the master branch or any other branch not up to date with kl-d7?" 
read answer
if echo "$answer" | grep -iq "^y" ;then
    	cp ocpca/ocpcaprivate.py.example ocpcaprivate.py
	cp django/OCP/settings_secret.py.example settings_secret.py
	cp django/OCP/settings.py.example settings.py

else
    	cp django/OCP/settings_secret.py.example settings_secret.py
	cp django/OCP/settings.py.example settings.py
	
fi

echo -n "Is this the first time you are setting up the server on this machine?" 
read answer
if echo "$answer" | grep -iq "^y" ;then
    	sudo mkdir /var/log/ocp
	sudo chown www-data:www-data /var/log/ocp
	sudo touch /var/log/ocp/ocp.log
	sudo chmod 777 /var/log/ocp/ocp.log

else
    	echo -n "If you experience issues with the log fies please run this step" 
fi



if [[ "$OSTYPE" == "linux-gnu" ]]; then
        cp /ocplib/makefile_LINUX /ocplib/makefile
	make -C /ocplib/
elif [[ "$OSTYPE" == "darwin"* ]]; then
        cp /ocplib/makefile_MAC /ocplib/makefile
	make -C /ocplib/
elif [[ "$OSTYPE" == "cygwin" ]]; then
        # POSIX compatibility layer and Linux environment emulation for Windows
	cp /ocplib/makefile_LINUX /ocplib/makefile
	make -C /ocplib/
elif [[ "$OSTYPE" == "msys" ]]; then
        # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
	echo -n "Unsupported Type"
elif [[ "$OSTYPE" == "win32" ]]; then
	echo -n "Unsupported Type"
        # I'm not sure this can happen.
elif [[ "$OSTYPE" == "freebsd"* ]]; then
        # ...
	echo -n "Unsupported Type"
else
        # Unknown.
	echo -n "Unsupported Type"
fi


python cython/Ocpca_cy/setup.py install
python cython/Zindex/setup.py install





