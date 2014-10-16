#m.PHONY : clean

all: clean ocplib.so

ocplib.so : filterCutout.o filterCutoutOMP.o locateCube.o annotateCube.o zindex.o recolorCube.o quicksort.o
	gcc -shared -fopenmp -O3 -o ocplib.so filterCutout.o filterCutoutOMP.o locateCube.o annotateCube.o zindex.o recolorCube.o quicksort.o -I .

filterCutout.o : filterCutout.c
	gcc -c -fPIC -O3 filterCutout.c -o filterCutout.o -I .

filterCutoutOMP.o : filterCutoutOMP.c
	 gcc -c -fopenmp -fPIC -O3 filterCutoutOMP.c -o filterCutoutOMP.o -I .

locateCube.o : locateCube.c
	gcc -c -fPIC -O3 locateCube.c -o locateCube.o -I .

annotateCube.o : annotateCube.c
	gcc -c -fPIC -O3 annotateCube.c -o annotateCube.o -I .

zindex.o : zindex.c
	gcc -c -fPIC -O3 zindex.c -o zindex.o -I .

recolorCube.o : recolorCube.c
	gcc -c -fopenmp -fPIC -O3 recolorCube.c -o recolorCube.o -I .

quicksort.o : quicksort.c
	gcc -c -fPIC -O3 quicksort.c -o quicksort.o -I .

test : clean testmain.c 
	gcc -ggdb testmain.c quicksort.c -o test -I .

clean :
	-rm -vf ocplib.so zindex.o locateCube.o annotateCube.o filterCutout.o filterCutoutOMP.o recolorCube.o test
