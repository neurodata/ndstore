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
 * Routines to converty to/from Morton-order z-index 
 */

#include<stdio.h>
#include<stdint.h>
#include<stdbool.h>
#include<stdlib.h>
#include<string.h>


// Generate morton order from XYZ coordinates

int XYZMorton ( uint32_t * xyz )
{
  int i;
  int morton = 0;

  uint32_t x = xyz[0];
  uint32_t y = xyz[1];
  uint32_t z = xyz[2];

  uint32_t mask = 0x001;

  // 21 triads of 3 bits each
	for ( i=0; i<21; i++ )
	{
    morton += ( x & mask ) << (2*i);
    morton += ( y & mask ) << (2*i+1);
    morton += ( z & mask ) << (2*i+2);

    mask <<= 1;
	}

  return morton;
}

// Generate XYZ coordinates from Morton index

void MortonXYZ ( int morton, int xyz[3] )
{
  int i;
  int xmask = 0x001;
  int ymask = 0x002;
  int zmask = 0x004;
  
  // 21 triads of 3 bits each
  for( i=0; i<21; i++)
  {
    xyz[0] += ( xmask & morton ) << i;
    xyz[1] += ( (ymask & morton) << i ) >> 1;
    xyz[2] += ( (zmask & morton) << i) >> 2;
    morton >>= 3;
  }

}
