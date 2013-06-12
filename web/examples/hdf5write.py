import subprocess

#command = "echo"
command = "/usr/bin/time"
filename = "h5post.py"
location = "localhost"
project = "kat11_syn1"
path = "~/kat11_synapses/anno"
outputfile = "timefile"

for i in range(4277,4280):
	subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,location,project,path+str(i)+".h5"])
