#include <iostream>

#include "region.hpp"
#include "fabvars.hpp"

using namespace std;

Region::Region()
    : imin(0), jmin(0), kmin(0),
      imax(0), jmax(0), kmax(0),
      ni(0), nj(0), nk(0),
      volume(0)
{
    // Nothing to do here
}

Region::Region(const FabVars& v)
    : imin(0), jmin(0), kmin(0),
      imax(v.ni - 1), jmax(v.nj - 1), kmax(v.nk - 1),
      ni(v.ni), nj(v.nj), nk(v.nk),
      volume(ni * nj * nk)
{
    // Nothing to do here.
}

Region::Region(unsigned int imin, unsigned int jmin, unsigned int kmin,
               unsigned int imax, unsigned int jmax, unsigned int kmax)
    : imin(imin), jmin(jmin), kmin(kmin),
      imax(imax), jmax(jmax), kmax(kmax),
      ni(imax - imin), nj(jmax - jmin), nk(kmax - kmin),
      volume(ni * nj * nk)
{
    // Nothing to do here.
}

list<Region> Region::split() const
{
    return split(2, 2, 2);
}

list<Region> Region::split(int isplit, int jsplit, int ksplit) const
{ 
    isplit = isplit > ni ? ni : isplit;
    jsplit = jsplit > nj ? nj : jsplit;
    ksplit = ksplit > nk ? nk : ksplit;
    
    list<Region> L;
    for (int k = ksplit - 1; k >= 0; --k)    
        for (int i = 0; i < isplit; ++i)
            for (int j = 0; j < jsplit; ++j)
                L.push_back(Region(imin + (i*ni) / isplit,
                                   jmin + (j*nj) / jsplit,
                                   kmin + (k*nk) / ksplit,
                                   imin + ((i+1)*ni) / isplit,
                                   jmin + ((j+1)*nj) / jsplit,
                                   kmin + ((k+1)*nk) / ksplit));
    return L;
}

// Split into a given number of segments (must be power of two),
// prioritizing larger dimensions
list<Region> Region::split(int count) const
{
    // We want to split along the longest dimension first
    int i_score = (ni >= nj) + (ni >= nk);
    int j_score = (nj >  ni) + (nj >= nk);
    int k_score = (nk >  ni) + (nk >  nj);
    
    // Adjust the split scores based on how many threads we support
    while ((1 << i_score) * (1 << j_score) * (1 << k_score) < count)
        if (i_score <= j_score && i_score <= k_score)
            ++i_score;
        else if (j_score < i_score && j_score <= k_score)
            ++j_score;
        else if (k_score < i_score && k_score < j_score)
            ++k_score;
    while ((1 << i_score) * (1 << j_score) * (1 << k_score) > count)
        if (k_score >= i_score && k_score >= j_score)
            --k_score;
        else if (j_score >= i_score && j_score > k_score)
            --j_score;
        else if (i_score > j_score && i_score > k_score)
            --i_score;

    return split(1<<i_score, 1<<j_score, 1<<k_score);
}

ostream& operator<<(ostream& o, const Region& r)
{
    o << "x: " << r.imin << " to " << r.imax << '\t'
      << "y: " << r.jmin << " to " << r.jmax << '\t'
      << "z: " << r.kmin << " to " << r.kmax << '\t';
    return o;
}