//
// path_ps.c
//    convert path to PostScript
//
// Neil Gershenfeld
// CBA MIT 9/1/10
//
// (c) Massachusetts Institute of Technology 2010
// Permission granted for experimental and personal use;
// license for commercial sale available from MIT.
//

#include "fab.h"

main(int argc, char **argv) {
   //
   // local vars
   //
   struct fab_vars v = init_vars(&v);
   struct fab_vars vnew = init_vars(&vnew);
   char view;
   int x,y,z,nz,dz;
   float scale;
   //
   // command line args
   //
   if (!((argc == 3) || (argc == 4))) {
      printf("command line: path_ps in.path out.ps [view]\n");
      printf("   in.path = input path file\n");
      printf("   out.ps= output PostScript file\n");
      printf("   view = view projection(s) (optional, z|3, default z)\n");
      exit(-1);
      }
   view = 'z';
   if (argc == 4)
      view = argv[3][0];
   //
   // read path
   //
   fab_read_path(&v,argv[1]);
   //
   // check view
   //
   if (view == 'z') {
      //
      // write ps
      //
      fab_write_ps(&v,argv[2]);
      }
   else if (view == '3') {
      if (v.path->dof < 3) {
         printf("path_ps: oops -- path not 3D\n");
         exit(-1);
         }
      nz = v.nx * v.dz / v.dx;
      scale = ((float) nz) / v.nz;
      vnew.nx = v.nx + nz;
      vnew.ny = v.ny + nz;
      vnew.nz = v.nz;
      vnew.dx = v.dx + v.dz;
      vnew.dy = v.dy + v.dz;
      vnew.dz = v.dz;
      vnew.xmin = v.xmin;
      vnew.ymin = v.ymin;
      vnew.zmin = v.zmin;
      fab_path_start(&vnew,v.path->dof);
      //
      // follow path
      //
      v.path->segment = v.path->first;
      while (1) {
         //
         // follow segments
         //
         v.path->segment->point = v.path->segment->first;
         fab_path_segment(&vnew);
         while (1) {
            //
            // follow points
            //
            fab_path_point(&vnew);
            z = v.path->segment->point->first->next->next->value;
            dz = nz - scale*z;
            y = dz + v.path->segment->point->first->next->value;
            x = dz + v.path->segment->point->first->value;
            fab_path_axis(&vnew,x);
            fab_path_axis(&vnew,y);
            fab_path_axis(&vnew,z);
            if (v.path->segment->point->next == 0)
               break;
            v.path->segment->point = v.path->segment->point->next;
            }
         if (v.path->segment->next == 0)
            break;
         v.path->segment = v.path->segment->next;
         }
      //
      // write ps
      //
      fab_write_ps(&vnew,argv[2]);
      }
   }

