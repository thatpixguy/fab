#ifndef EDGESOLVER_H
#define EDGESOLVER_H

#include <map>
#include <utility>
#include <boost/thread.hpp>

#include "fabvars.hpp"
#include "math_tree.hpp"
#include "region.hpp"
#include "geometry.hpp"

class EdgeSolver
{
public:
    typedef std::list<std::pair<boost::thread*, EdgeSolver*> > ThreadList;

    static void evaluate(MathTree* tree, FabVars& v);
    static void make_new_thread(MathTree* T, Region R,
                                FabVars& v, ThreadList& thread_list);
    static void wait_for_threads(ThreadList& thread_list);


    EdgeSolver(MathTree* tree, FabVars& v);

    void evaluate_region(Region R);
    void evaluate_voxel(Region R);

    void save_edges();
    
    Vec3f interpolate(Vec3f filled, Vec3f empty);

private:    
    MathTree* tree;
    FabVars& v;
    std::map<Vec3f, bool> point_cache;
    std::map<Edge, Vec3f> edge_cache;
    PathSet paths;

};
#endif