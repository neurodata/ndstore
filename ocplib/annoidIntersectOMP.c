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

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>

int cmpFunc ( const void * a, const void * b )
{
  return ( *(int*)a - *(int*)b );
}

void annoidIntersect ( uint32_t * cutout, int cutoutsize, uint32_t * annoidlist, int listsize )
{
  int i, j, k, cutout=0;
  qsort( cutout, cutoutsize, sizeof(uint32_t), cmpFunc )

  for ( i=0; i<cutoutsize; i++)
  {
    for (j=0, j<count; j++)
    {
      if(cutout[i] == cutout[j])
        break;
    }
    if( j == count )
    {
      cutout[j] = cutout[i];
      count++
    }
  }

  i=0, j=0, k=0;
  while ((i < count) && (j < listsize))
  {
    if (cutout[i] < annoidlist[j])
      i++;
    else if (cutout[i] > annoidlist[j])
      j++;
    else
    {
      intersection_array[k] = array1[i];
      i++;
      j++;
      k++;
    }
  }
}
