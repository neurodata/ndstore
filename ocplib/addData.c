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
 * Add Data Functions
 * Naive implementation 
 */

#include<stdint.h>
#include<ocplib.h>

// Determine the annotation value at the next level of the hierarchy from a 2x2

int getAnnValue ( uint32_t value00, uint32_t value01, uint32_t value10, uint32_t value11 )
{
  int value = value00;

  if ( value == 0 )
    value = value01;

  if ( value10 != 0 )
    if ( value == 0 )
      value = value10;
    else if ( value10 == value00 || value10 == value01 )
      value = value10;

  if ( value11 != 0 )
    if ( value ==0 )
      value = value10;
    else if ( value11==value00 || value11==value01 || value11==value10 )
      value = value11;

  return value;
}


// Add the contribution of the input data to the next level at the given offset in the output cube

void addDataZSlice ( uint32_t * cube, uint32_t * output, int * offset, int * dims )
{
  int i,j,k;

  int xdim = dims[0];
  int ydim = dims[1];
  int zdim = dims[2];

  for ( i=0; i<zdim; i++ )
    for ( j=0; j<ydim/2; j++ )
      for ( k=0; k<xdim/2; k++ )
      {
        int index1 = (i*ydim*xdim)+(j*2*xdim)+(k*2);
        int index2 = (i*ydim*xdim)+(j*2*xdim)+(k*2+1);
        int index3 = (i*ydim*xdim)+(j*2*xdim+1)+(k*2);
        int index4 = (i*ydim*xdim)+(j*2*xdim+1)+(k*2+1);
        int outputindex = (i*ydim*xdim+offset[2])+(j*xdim+offset[1])+(k+offset[0]);
        output[outputindex] = getAnnValue ( cube[index1], cube[index2], cube[index3], cube[index4] );
      }
}


// Add the contribution of the input data to the next level at the given offset in the output cube

void addDataIsotropic ( uint32_t * cube, uint32_t * output, int * offset, int * dims )
{
  int i,j,k;

  int xdim = dims[0];
  int ydim = dims[1];
  int zdim = dims[2];

  for ( i=0; i<zdim/2; i++ )
    for ( j=0; j<ydim/2; j++ )
      for ( k=0; k<xdim/2; k++ )
      {
        continue;
      }
}
