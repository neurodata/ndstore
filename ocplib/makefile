#m.PHONY : clean

all: clean ocplib.so

ocplib.so : filterCutout.o filterCutoutOMP.o locateCube.o annotateCube.o zindex.o recolorCube.o
	gcc -shared -fopenmp -o ocplib.so filterCutout.o filterCutoutOMP.o locateCube.o annotateCube.o zindex.o recolorCube.o -I .

filterCutout.o : filterCutout.c
	gcc -c -fPIC filterCutout.c -o filterCutout.o -I .

filterCutoutOMP.o : filterCutoutOMP.c
	 gcc -c -fopenmp -fPIC filterCutoutOMP.c -o filterCutoutOMP.o -I .

locateCube.o : locateCube.c
	gcc -c -fPIC locateCube.c -o locateCube.o -I .

annotateCube.o : annotateCube.c
	gcc -c -fPIC annotateCube.c -o annotateCube.o -I .

zindex.o : zindex.c
	gcc -c -fPIC zindex.c -o zindex.o -I .

recolorCube.o : recolorCube.c
	gcc -c -fopenmp -fPIC recolorCube.c -o recolorCube.o -I .

test : clean testmain.c
	gcc -fopenmp -ggdb -o test testmain.c zindex.c locateCube.c -I .

clean :
	-rm -vf ocplib.so zindex.o locateCube.o annotateCube.o filterCutout.o filterCutoutOMP.o recolorCube.o test
