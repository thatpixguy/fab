#ifndef FABTOOLS_H
#define FABTOOLS_H

#include <string>
#include <fstream>
#include <list>

#include <cstdlib>
#include <stdint.h>

#include <boost/thread.hpp>

#include "fab_interval.hpp"
#include "geometry.hpp"
#include "region.hpp"

enum solver_mode { SOLVE_BOOL, SOLVE_RGB, SOLVE_REAL };
enum output_mode { OUTPUT_PNG, OUTPUT_STL, OUTPUT_SVG, OUTPUT_NONE };

typedef struct FabVars {
    FabVars(output_mode o);
    ~FabVars();
    void load();
    
    void fill(Region r);
    void fill(Region r, unsigned char R, unsigned char G, unsigned char B);
    
    void add_triangle(Vec3f v1, Vec3f v2, Vec3f v3);
    void add_triangles(std::list<Triangle> tris);
    void add_paths(const PathSet& p);
    
    void write_png();
    void write_png(std::string filename);
    void write_stl();
    void write_svg();
    
    // Convert from pixel coordinates to real coordinates
    float x(float i) const;
    float y(float j) const;
    float z(float k) const;

    // Convert from pixel interval to real interval
    FabInterval x(float imin, float imax) const;
    FabInterval y(float jmin, float jmax) const;
    FabInterval z(float kmin, float kmax) const;
    
    float scale(unsigned int k) const;
    
    int ni,nj,nk; // Distances in pixels
    int min_volume; // Minimum volume for octree
    
    double dx,dy,dz; // Position and size in arbitrary cad units
    double xmin,ymin,zmin;
    
    double pixels_per_mm;
    double mm_per_unit;
    int quality;
    float stroke;
    float decimation_error;
    
    solver_mode mode;
    output_mode output;
    std::string infile_name;
    std::string outfile_name;
    
    uint8_t **red,**green,**blue;
    uint16_t **intensity;
    
    std::string math_string;
    
    boost::mutex geometry_lock;
    std::list<Triangle> triangles;
    PathSet paths;
    
} FabVars;

void fab_write_png_K16(FabVars* v, const char* output_file_name);
void fab_write_png_RGB24(FabVars* v, const char* output_file_name);

#endif
