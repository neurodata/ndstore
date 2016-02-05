/*
* Copyright 2014 NeuroData (http://neurodata.io)
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
 * Unique Function 
 * Naive implementation 
 */

#include<stdint.h>
#include<stdlib.h>
#include<ndlib.h>

int cmpFunc32 ( const void * pa, const void * pb )
{
  return ( *(const uint32_t*)pa - *(const uint32_t*)pb );
}

// Naive Implementation of Quicksort

void quicksort32 ( uint32_t * data, int dataSize )
{
  qsort ( data , dataSize, sizeof(uint32_t), cmpFunc32 );
}


int unique( uint32_t * data, uint32_t * unique_array, int dataSize )
{
  int i,index=0;
  
  quicksort32 ( data, dataSize );
  
  for ( i=0; i<dataSize; i++ )
  {
    while ( i<dataSize-1 && data[i] == data[i+1] )
      i++;
   
    unique_array[index] = data[i];
    index++;
  }

  return index;
}
