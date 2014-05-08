#m.PHONY : clean

all: clean filterCutout.so filterCutoutOMP.so

naive : clean filterCutout.so

openmp : clean filterCutoutOMP.so

filterCutout.so : filterCutout.o
	gcc -shared -o filterCutout.so filterCutout.o -I .

filterCutout.o : filterCutout.c
	gcc -c -fPIC filterCutout.c -o filterCutout.o -I .

filterCutoutOMP.so : filterCutoutOMP.o
	gcc -fopenmp -shared -o filterCutoutOMP.so filterCutoutOMP.o -I .

filterCutoutOMP.o : filterCutoutOMP.c
	 gcc -c -fopenmp -fPIC filterCutoutOMP.c -o filterCutoutOMP.o -I .

test : testmain.c
	gcc -fopenmp -ggdb -o test testmain.c filterCutout.c filterCutoutOMP.c -I .

clean :
	-rm -vf filterCutout.so filterCutout.o filterCutoutOMP.so filterCutoutOMP.o test
