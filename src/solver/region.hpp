#ifndef REGION_H
#define REGION_H

#include <list>

// Forward declarations
struct FabVars;

// A note on terminology:
//      x, y, z refer to coordinates in space.
//      i, j, k refer to pixel discretized coordinates

typedef struct Region {
    Region(const FabVars& v);
    Region(const FabVars& v,
           unsigned int imin, unsigned int jmin, unsigned int kmin,
           unsigned int imax, unsigned int jmax, unsigned int kmax);
    
    std::list<Region> split() const;
    std::list<Region> split(int count) const;
    std::list<Region> split(int isplit, int jsplit, int ksplit) const;
    
    const FabVars& v;
    int imin, jmin, kmin, imax, jmax, kmax;
    int ni, nj, nk;
    long volume;
    
} Region;
std::ostream& operator<<(std::ostream& o, const Region& r);

#endif