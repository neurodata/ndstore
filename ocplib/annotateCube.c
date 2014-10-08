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
 * Annotate Cube Function 
 * Naive implementation 
 */

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>
#include<stdlib.h>
#include<string.h>

int annotateCube( uint32_t * data, int dataSize, int * dims, int annid, int * offset,  uint32_t * locations, int locationsSize, char conflictopt, uint32_t * exceptions )
{
		int i,j;
    int index;
    int xoffset = offset[0];
    int yoffset = offset[1];
    int zoffset = offset[2];

    int xdim = dims[0];
    int ydim = dims[1];
    int zdim = dims[2];

    int exceptionIndex = -1;

		for ( i=0; i<locationsSize; i+=3)
		{

      index = (locations[i+2]-zoffset)*(ydim*zdim) + (locations[i+1]-yoffset)*(zdim) + (locations[i]-xoffset);

      // Label unlabeled voxels
      
      if ( data [ index ] == 0 )
      {
        data [ index ] == annid;
      }
      
      // Already labelled voxels are exceptios, unless they are the same value
      else if ( data [ index ] !=annid )
      {
        // 0 is for overwrite
        if ( conflictopt == 'O' )
        {
          data [ index ] = (uint32_t)annid;
        }
        // P preserves the existing content
        else if ( conflictopt == 'P' )
          continue;
        // E creates exceptions
        else if ( conflictopt == 'E' )
          printf ( "Append exceptions" );
          exceptions [ ++exceptionIndex ] = locations[i]-xoffset;
          exceptions [ ++exceptionIndex ] = (locations[i+1]-yoffset)*(zdim);
          exceptions [ ++exceptionIndex ] = (locations[i+2]-zoffset)*(ydim*zdim);
      }
      else
      {
        printf ( "Improper conflict option selected. Option = %c", conflictopt );
        //assert(0);
      }
      
      return exceptionIndex;

		}
}
