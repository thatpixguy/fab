#ifndef SOLVER_H
#define SOLVER_H

#include <boost/thread.hpp>

#include "fabvars.hpp"
#include "math_tree.hpp"
#include "region.hpp"

class Solver
{
public:
    Solver(FabVars& v);
    void evaluate(MathTree* tree);
    void evaluate_regions(MathTree* tree, std::list<Region> regions);
    void evaluate_region(MathTree* tree, Region R);
    void evaluate_points(MathTree* tree, Region R);
    void evaluate_array(MathTree* tree, Region R);

private:
    typedef std::list<std::pair<boost::thread*, MathTree*> > ThreadList;
    
    void make_new_thread(MathTree* T, Region R,
                         ThreadList& thread_list);
    void wait_for_threads(ThreadList& thread_list);
    void cull_regions(std::list<Region>& subregions);
    
    FabVars& v;
    const int MAX_THREADS;
    
    // Variables related to the output progress bar
    unsigned long full_volume;
    unsigned long solved_volume;
    int next_tick;
    int bar_length;
    boost::mutex solved_volume_lock;
    void update_progress(long dVol);
};
#endif