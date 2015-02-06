/*
* Copyright 2014 Open Connectome Project (http://openconnecto.me)
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* 
*     http://www.apache.org/licenses/LICENSE-2.0
* 
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/


/*
 * Zoom Data Functions
 * Naive implementation 
 */

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>
#include<stdlib.h>
#include<string.h>
#include<math.h>
#include<omp.h>

void zoomOutData( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i,j,k;

    int zdim = dims[0];
    int ydim = dims[1];
    int xdim = dims[2];
   
    int oldindex,newindex;
    int power = pow(2,factor);

		for ( i=0; i<zdim; i++ )
      for ( j=0; j<ydim; j++ )
        for ( k=0; k<xdim; k++ )
        {
          newindex = (i*xdim*ydim)+(j*xdim)+(k);
          oldindex = ( i*(xdim*power)*(ydim*power) ) + ( (j*power)*(xdim*power) ) + ( k*power );
          newdata[newindex] = olddata[oldindex];
        }
}


void zoomOutDataOMP( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i,j,k;

    int zdim = dims[0];
    int ydim = dims[1];
    int xdim = dims[2];
   
    int oldindex,newindex;
    int power = pow(2,factor);

    printf("MAX THREADS: %d",omp_get_max_threads());

#pragma omp parallel num_threads(omp_get_max_threads())
    {
#pragma omp for private(i,j,k) schedule(dynamic)
      for ( i=0; i<zdim; i++ )
        for ( j=0; j<ydim; j++ )
          for ( k=0; k<xdim; k++ )
          {
            newindex = (i*xdim*ydim)+(j*xdim)+(k);
            oldindex = ( i*(xdim*power)*(ydim*power) ) + ( (j*power)*(xdim*power) ) + ( k*power );
            newdata[newindex] = olddata[oldindex];
          }
    }
}


void zoomInData( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i,j,k;

    int zdim = dims[0];
    int ydim = dims[1];
    int xdim = dims[2];
   
    int oldindex,newindex;
    int power = pow(2,factor);

		for ( i=0; i<zdim; i++ )
      for ( j=0; j<ydim; j++ )
        for ( k=0; k<xdim; k++ )
        {
          newindex = (i*xdim*ydim)+(j*xdim)+(k);
          oldindex = ( i*(xdim/power)*(ydim/power) ) + ( (j/power)*(xdim/power) ) + ( k/power );
          if ( oldindex > (zdim*xdim*ydim)/(pow(2,factor)*pow(2,factor)) )
          {  
            printf("%d %d %d %d \n",i,j,k,oldindex);
          }
          newdata[newindex] = olddata[oldindex];
        }
}


void zoomInDataOMP( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i,j,k;

    int zdim = dims[0];
    int ydim = dims[1];
    int xdim = dims[2];
   
    int oldindex, newindex;
    int power = pow(2,factor);
    printf("MAX THREADS: %d",omp_get_max_threads());

#pragma omp parallel num_threads(omp_get_max_threads())
    {
#pragma omp for private(i,j,k) schedule(dynamic)
      for ( i=0; i<zdim; i++ )
        for ( j=0; j<ydim; j++ )
          for ( k=0; k<xdim; k++ )
          {
            newindex = (i*xdim*ydim)+(j*xdim)+(k);
            oldindex = ( i*(xdim/power)*(ydim/power) ) + ( (j/power)*(xdim/power) ) + ( k/power );
            newdata[newindex] = olddata[oldindex];
          }
    }
}
