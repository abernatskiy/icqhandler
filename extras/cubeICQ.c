/* Author: Lindsey Koelbel
   Date created: 08/29/2018
   This function will generate an ICQ shapefile of a cube centered at the origin with resolution size Q and side length L.  */

#include <stdio.h>
#include <math.h>
#include <stdlib.h>


int main (void){
  FILE *icq; //This variable will hold the file we are writing to
  icq = fopen("icq.txt", "w"); //open file for writing, will create a file or overwrite an existing file


  int Q = 4; //Define resolution
  float L = 30.0; //Side length of cube (in kilometers)
  fprintf(icq, "\t     %d\n",Q); //Prints the first line of the ICQ, which is just the resolution size
  float i, j, k; //One variable to track each component of the cartesian coordinates


  //Writing vertices for face 1
  k = (L / 2);
  for (j = -(L / 2); j <= (L / 2); j = j + (L / Q)){
    for (i = (L / 2); i >= -(L / 2); i = i - (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
  //Writing vertices for face 2
  j = (L / 2);
  for (k = (L / 2); k >= -(L / 2); k = k - (L / Q)){
    for (i = (L / 2); i >= -(L / 2); i = i - (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
  //Writing vertices for face 3
  i = (L / 2);
  for (k = (L / 2); k >= -(L / 2); k = k - (L / Q)){
    for (j = -(L / 2); j <= (L / 2); j = j + (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
  //Writing vertices for face 4
  j = -(L / 2);
  for (k = (L / 2); k >= -(L / 2); k = k - (L / Q)){
    for (i = -(L / 2); i <= (L / 2); i = i + (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
  //Writing vertices for face 5
  i = -(L / 2);
  for (k = (L / 2); k >= -(L / 2); k = k - (L / Q)){
    for (j = (L / 2); j >= -(L / 2); j = j - (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
  //Writing vertices for face 6
  k = -(L / 2);
  for (j = (L / 2); j >= -(L / 2); j = j - (L / Q)){
    for (i = (L / 2); i >= -(L / 2); i = i - (L / Q)){
      fprintf(icq, "\t%f\t%f\t%f\n", i, j, k);
    }
  }
}
