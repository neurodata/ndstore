/*
 * Testing Function for Filter
 * Usage: 	1 - Naive Implementation
 * 		 	2 - OpenMP Implementation
 */ 		 	

#include<stdio.h>
#include<stdint.h>
#include<filter.h>

void main(int argc, char * argv[])
{
		uint32_t samplearray[10] = {1,1,9,2,3,1,2,6,9.0};
		uint32_t filterarray[3] = {2,3,4};

		if(strcmp(argv[1],"naive") == 0)
		{
				printf("Using naive implementation");
				filterCutout(samplearray,10,filterarray,3);
		}
		else if(strcmp(argv[1],"openmp") == 0)
		{
				printf("Using openmp implementation");
				filterCutoutOMP(samplearray,10,filterarray,3);
		}

		int i;
		for(i=0;i<10;i++)
				printf("%4u \n",samplearray[i]);
}
