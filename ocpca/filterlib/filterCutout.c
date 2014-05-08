/*
 * Filter Cutout Function 
 * Naive implementation 
 */

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>

void filterCutout( uint32_t * cutout, int cutoutsize, uint32_t * filterlist, int listsize)
{
		int i,j;
		bool equal;

		for ( i=0; i<cutoutsize; i++)
		{
				equal = false;
				for ( j=0; j<listsize; j++)
				{
					// Checking if element in cutout exits in filterlist	
					if( cutout[i] == filterlist[j] )
					{
							equal = true;
							// Using break to exit because it exists in the list
							break;
					}
				}
				if( !equal )
						cutout[i] = 0;
		}
}
