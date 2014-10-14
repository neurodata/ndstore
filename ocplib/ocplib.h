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
 * Header File for OCP Ctype Functions
*/
 
#include<stdint.h>

// Declaring Naive implementation for filterCutout
void filterCutout ( uint32_t * , int , uint32_t *, int );

// Declaring the OpenMP implementation for filterCutout
void filterCutoutOMP ( uint32_t *, int , uint32_t *, int );

// Decalring the OpenMP cache optimized implementation for filterCutout
void filterCutoutOMPCache ( uint32_t *, int, uint32_t *, int );

// Declaring the annotateCube implementation
int annotateCube ( uint32_t * , int , int * , int , int * , uint32_t [][3] , int , char, uint32_t [][3] );

// Declaring the locateCube implementation
void locateCube ( uint32_t [][4] , int , uint32_t [][3] , int , int * );

// Declaring XYZMorton zindex function
int XYZMorton ( uint32_t * );

// Declaring MortonXYZ zindex function
void MortonXYZ ( int , int [3] );

// Declaring recolorSlice function
void recolorSlice ( uint32_t * , int , int , uint32_t * , uint32_t * ); 
