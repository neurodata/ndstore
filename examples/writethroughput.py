import subprocess

command = "echo"
#command = "/usr/bin/time"
filename = "denseannotest.py"
baseurl = "localhost"
dataset = "ac3"
token = "ac3_test1"
resolution = "1"
outputfile = "timefile"

# 128 * 128 * 16

xlow = 5472
xhigh = 6496
ylow = 8712
yhigh = 9736
zlow = 1000
zhigh = 1255
xoffset = 128
yoffset = 128
zoffset = 16
#subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xhigh),str(ylow),str(yhigh),str(zlow),str(zhigh)])

#128 x 128 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset),str(ylow),str(ylow+yoffset),str(zlow),str(zlow+zoffset)])

#256 x 128 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*2),str(ylow),str(ylow+yoffset),str(zlow),str(zlow+zoffset)])

#512 x 128 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*4),str(ylow),str(ylow+yoffset),str(zlow),str(zlow+zoffset)])


#1024 x 128 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset),str(zlow),str(zlow+zoffset)])

#1024 x 256 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*2),str(zlow),str(zlow+zoffset)])

#1024 x 512 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*4),str(zlow),str(zlow+zoffset)])

#1024 x 1024 x 16
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*8),str(zlow),str(zlow+zoffset)])

#1024 x 1024 x 32
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*8),str(zlow),str(zlow+zoffset*2)])

#1024 x 1024 x 64
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*8),str(zlow),str(zlow+zoffset*4)])

#1024 x 1024 x 128
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*8),str(zlow),str(zlow+zoffset*8)])

#1024 x 1024 x 64
subprocess.call([command,"-p","--output="+outputfile,"--append","python",filename,baseurl,dataset,token,resolution,str(xlow),str(xlow+xoffset*8),str(ylow),str(ylow+yoffset*8),str(zlow),str(zlow+zoffset*16)])







