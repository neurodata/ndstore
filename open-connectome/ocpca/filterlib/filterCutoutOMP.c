#include<stdio.h>
#include<stdint.h>
#include<omp.h>
#include<stdbool.h>

void filterCutoutOMP( uint32_t * cutout, int cutoutsize, uint32_t * filterlist, int listsize)
{
		int i,j;
		bool equal;
		printf("MAX THREADS: %d",omp_get_max_threads());
#pragma omp parallel num_threads(omp_get_max_threads()) 
		{
#pragma omp for private(i,j,equal) schedule(dynamic)
				for ( i=0; i<cutoutsize; i++)
				{
						equal = false;
						for( j=0; j<listsize; j++)
						{
								if( cutout[i] == filterlist[j] )
								{
										equal = true;
										break;
								}
						}
						if( !equal )
								cutout[i] = 0;
				}
		int ID = omp_get_thread_num();
		printf("THREAD ID: %d",ID);
		}
}
