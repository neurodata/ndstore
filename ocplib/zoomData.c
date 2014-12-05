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

void zoomOutData( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i;
    int j;
    int k;

    int xdim = dims[0];
    int ydim = dims[1];
    int zdim = dims[2];
   
    int oldindex;
    int newindex;

		for ( i=0; i<zdim; i++ )
      for ( j=0; j<ydim; j++ )
        for ( k=0; k<xdim; k++ )
        {
          newindex = (i*xdim*ydim)+(j*xdim)+(k);
          oldindex = (i*xdim*ydim)+(j*xdim*pow(2,factor))+(k*pow(2,factor));
          newdata[newindex] = olddata[oldindex];
        }
}


void zoomInData( uint32_t * olddata, uint32_t * newdata, int * dims, int factor )
{
		int i;
    int j;
    int k;

    int xdim = dims[0];
    int ydim = dims[1];
    int zdim = dims[2];
   
    int oldindex;
    int newindex;

		for ( i=0; i<zdim; i++ )
      for ( j=0; j<ydim; j++ )
        for ( k=0; k<xdim; k++ )
        {
          newindex = (i*xdim*ydim)+(j*xdim)+(k);
          oldindex = (i*xdim*ydim)+(j*xdim/pow(2,factor))+(k/pow(2,factor));
          newdata[newindex] = olddata[oldindex];
        }
}
