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
 * Quick Sort Implementation in C using OpenMP 
 */

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>
#include<stdlib.h>
#include<string.h>

// cmpFunc for QuickSort

int cmpFunc ( const uint32_t a[4], const uint32_t b[4] )
{
  //uint32_t x[4] = ( uint32_t * )a;
  //uint32_t y[4] = ( uint32_t * )b;

  if ( a[0] < b[0] )
    return -1;
  else if ( a[0] > b[0] )
    return 1;
  else if ( a[0] == b[0] )
  {
    if ( a[1] < b[1] )
      return -1;
    else if( a[1] > b[1] )
      return 1;
    else if ( a[1] == b[1] )
    {
      if ( a[2] < b[2] )
        return -1;
      else if ( a[2] > b[2] )
        return 1;
      else if ( a[2] == b[2] )
      {
        if ( a[3] < b[3] )
          return -1;
        else if ( a[3] > b[3] )
          return 1;
        else
          return 0;
      }
    }
  }
  //return ( *(uint32_t *)a[0] - *(uint32_t *)b[0] );
}

// Naive Implementation of Quicksort

void quicksort ( uint32_t locs[][4], int locsSize )
{
  int i;
  
  qsort ( locs , locsSize, 4*sizeof(uint32_t), cmpFunc );

}

