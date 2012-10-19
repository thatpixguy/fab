#include "edgesolver.hpp"
#include "node.hpp"
#include "switches.hpp"
#include "geometry.hpp"

#include <iostream>
#include <cstdio>

using namespace std;
using boost::logic::tribool;
using boost::thread;

const Vec3f OFFSETS[] = {
    Vec3f(0, 0), Vec3f(1, 0), Vec3f(1, 1), Vec3f(0, 1)
};

const int EDGE_MAP[16][2][2] = {
    {{-1,-1}, {-1,-1}}, // ----
    {{ 0, 1}, { 0, 3}}, // ---0
    {{ 1, 2}, { 1, 0}}, // --1-
    {{ 1, 2}, { 0, 3}}, // --10
    {{ 2, 3}, { 2, 1}}, // -2--
    {{-2,-2}, {-2,-2}}, // -2-0
    {{ 2, 3}, { 1, 0}}, // -21-
    {{ 2, 3}, { 0, 3}}, // -210
    
    {{ 3, 0}, { 3, 2}}, // 3---
    {{ 0, 1}, { 3, 2}}, // 3--0
    {{-2,-2}, {-2,-2}}, // 3-1-
    {{ 1, 2}, { 3, 2}}, // 3-10
    {{ 3, 0}, { 2, 1}}, // 32--
    {{ 0, 1}, { 2, 1}}, // 32-0
    {{ 3, 0}, { 1, 0}}, // 321-
    {{-1,-1}, {-1,-1}} // 3210
};
///////////////////////////////////////////////////////////////////////////////

void EdgeSolver::evaluate(MathTree* tree, FabVars& v)
{
#if MULTITHREADED
    list<Region> regions = Region(v).split(thread::hardware_concurrency());
    
    // This thread needs something to do while waiting for the other threads
    // to run - pick the first region as this thread's task.
    Region mine = regions.front();
    regions.pop_front();

    // Create a thread for each region
    ThreadList thread_list;
    list<Region>::iterator it;
    for (it = regions.begin(); it != regions.end(); ++it)
        make_new_thread(tree, *it, v, thread_list);

    // Evaluate this thread's region
    EdgeSolver e(tree, v);
    e.evaluate_region(mine);
    e.save_edges();
    
    wait_for_threads(thread_list);
#else
    EdgeSolver e(tree, v);
    e.evaluate_region(Region(v));
    e.save_edges();
#endif
}

///////////////////////////////////////////////////////////////////////////////

void EdgeSolver::make_new_thread(MathTree* T, Region R, FabVars& v,
                                ThreadList& thread_list)
{
    thread* newThread = new thread;
    MathTree* newTree = T->clone();
    EdgeSolver* e = new EdgeSolver(newTree, v);

    *newThread = thread(&EdgeSolver::evaluate_region, e, R);
    thread_list.push_back(make_pair(newThread, e));
}

///////////////////////////////////////////////////////////////////////////////

void EdgeSolver::wait_for_threads(ThreadList& thread_list)
{
    while (!thread_list.empty())
    {
        ThreadList::iterator it = thread_list.begin();
        while(it != thread_list.end())
            if (it->first->timed_join(boost::system_time()))
            {
                delete it->first;
                it->second->save_edges();
                delete it->second->tree;
                delete it->second;
                it = thread_list.erase(it);
            } else {
                ++it;
            }
    }
}



///////////////////////////////////////////////////////////////////////////////

EdgeSolver::EdgeSolver(MathTree* tree, FabVars& v)
    : tree(tree), v(v), paths(v.decimation_error)
{
    // Nothing to do here.
}

void EdgeSolver::save_edges()
{
    v.add_paths(paths);
}

// Evaluate a single region, either with point-by-point evaluation or
// interval math + recursion.  Operates in a single thread and spawns
// no children.
void EdgeSolver::evaluate_region(Region r)
{  
    // For sufficiently small fractions of the space, do a
    // point-by-point evaluation rather than recursing.
    if (r.volume == 1) {
        evaluate_voxel(r);
        return;
    }
    
    // Convert from pixel regions to intervals
    FabInterval X = v.x(r.imin, r.imax);
    FabInterval Y = v.y(r.jmin, r.jmax);
    FabInterval Z = v.z(r.kmin, r.kmax);

    tree->eval(X, Y, Z);
    
    // If the result was unambiguous, then fill in that part
    // of the image, then return.
    tribool result = tree->root->result_bool;
    
    if (!indeterminate(result))
        return;

    // Split the region and recurse
    list<Region> subregions = r.split();

#if PRUNE_TREE
    tree->push();
#endif

    list<Region>::iterator it;
    for (it = subregions.begin(); it != subregions.end(); ++it)
        evaluate_region(*it);

#if PRUNE_TREE
    tree->pop();
#endif
}

///////////////////////////////////////////////////////////////////////////////

void EdgeSolver::evaluate_voxel(Region r)
{
    Vec3f corner(r.imin, r.jmin, r.kmin);
    Vec3f v1, v2; // edge vertices
    
    Vec3f vertices[4];
    for (int i = 0; i < 4; ++i)
        vertices[i] = corner + OFFSETS[i];
        
    int lookup = 0;
    for (int i = 3; i >= 0; --i) {
        lookup <<= 1;
        Vec3f pos = vertices[i];
        
        if (point_cache.find(pos) == point_cache.end()) {
            tree->eval(v.x(pos.x), v.y(pos.y), v.z(pos.z));
            point_cache[pos] = tree->root->result_bool;        
        }
        
        if (point_cache[pos])
            lookup++;
    }    
    
    if (EDGE_MAP[lookup][0][0] == -1)
        return;
    if (EDGE_MAP[lookup][0][0] == -2)
        return;
    
    v1 = interpolate(vertices[EDGE_MAP[lookup][0][0]],
                     vertices[EDGE_MAP[lookup][0][1]]);
    v2 = interpolate(vertices[EDGE_MAP[lookup][1][0]],
                     vertices[EDGE_MAP[lookup][1][1]]);
    paths += Path(v1, v2);
           
}

Vec3f EdgeSolver::interpolate(Vec3f filled, Vec3f empty)
{
    std::map<Edge, Vec3f>::iterator it;
    it = edge_cache.find(Edge(filled, empty));
    if (it != edge_cache.end())
        return it->second;
        
    float step_size = 0.25;
    float interp = 0.5;
    Vec3f offset = empty - filled;
    
    for (int i = 0; i < v.quality; ++i) {
        Vec3f pos = filled + offset * interp;
    
        tree->eval(v.x(pos.x), v.y(pos.y), v.z(pos.z));
        if (tree->root->result_bool)
            interp += step_size;
        else
            interp -= step_size;
        step_size /= 2;
    }
    edge_cache[Edge(filled, empty)] = filled + offset * interp;
    
    return filled + offset * interp;
}