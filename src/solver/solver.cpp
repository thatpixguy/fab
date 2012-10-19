#include "solver.hpp"
#include "node.hpp"
#include "switches.hpp"

using namespace std;
using boost::logic::tribool;
using boost::thread;

Solver::Solver(FabVars& v)
    : v(v), MAX_THREADS(thread::hardware_concurrency()),
      full_volume(v.ni * v.nj * v.nk), solved_volume(0),
      next_tick(1), bar_length(40)
{
    // Nothing to do here.
}

///////////////////////////////////////////////////////////////////////////////

void Solver::evaluate(MathTree* tree)
{
#if MULTITHREADED
    evaluate_regions(tree, Region(v).split(MAX_THREADS));
#else
    evaluate_region(tree, Region(v));
#endif
}

// Evaluate a list of regions by assigning each region to a separate thread
// (reserving the first region for the current thread)
void Solver::evaluate_regions(MathTree* tree, list<Region> regions)
{
    ThreadList thread_list;
    
    // This thread needs something to do while waiting for the other threads
    // to run - pick the first region as this thread's task.
    Region mine = regions.front();
    regions.pop_front();

    // Create a thread for each region
    list<Region>::iterator it;
    for (it = regions.begin(); it != regions.end(); ++it)
        make_new_thread(tree, *it, thread_list);

    // Evaluate this thread's region
    evaluate_region(tree, mine);
    
    wait_for_threads(thread_list);
}

// Evaluate a single region, either with point-by-point evaluation or
// interval math + recursion.  Operates in a single thread and spawns
// no children.
void Solver::evaluate_region(MathTree* tree, Region r)
{  
    // For sufficiently small fractions of the space, do a
    // point-by-point evaluation rather than recursing.
    if (r.volume > 0 && r.volume <= v.min_volume) {
        evaluate_points(tree, r);
        update_progress(r.volume);
        return;
    }
    
    // Convert from pixel regions to intervals
    FabInterval X = v.x(r.imin, r.imax);
    FabInterval Y = v.y(r.jmin, r.jmax);
    FabInterval Z = v.z(r.kmin, r.kmax);

    tree->eval(X, Y, Z);
    // If the result was unambiguous, then fill in that part
    // of the image, then return.
    if (v.mode == SOLVE_BOOL) {
        tribool result = tree->root->result_bool;
        if (result)
            v.fill(r);
        
        if (!indeterminate(result)) {
            update_progress(r.volume);
            return;
        }
        
    } else if (v.mode == SOLVE_RGB) {
        int result = tree->root->result_color;
        if (result != -1) {
            v.fill(r, result & 255,
                     (result >> 8) & 255,
                     (result >> 16) & 255);
            update_progress(r.volume);
            return;
        }
    }

    // Split the region and recurse
    list<Region> subregions = r.split();

#if CULL_Z
    if (v.nk > 1)
        cull_regions(subregions);
    if (subregions.size() == 0)
        return;
#endif

#if PRUNE_TREE
    tree->push();
#endif

    list<Region>::iterator it;
    for (it = subregions.begin(); it != subregions.end(); ++it)
        evaluate_region(tree, *it);

#if PRUNE_TREE
    tree->pop();
#endif
}

///////////////////////////////////////////////////////////////////////////////

// Evalutes a region full of points, one at a time.
void Solver::evaluate_points(MathTree* tree, Region r)
{
    for (int k = r.kmax - 1; k >= r.kmin; --k)
    {
    
        // Calculate Z coordinate and height-map scaling.
        float Z = v.z(k);
        float scale = v.scale(k);
        
        for (int i = r.imin; i < r.imax; ++i)
        { // X loop
            float X = v.x(i);
            
            for (int j = r.jmin; j < r.jmax; ++j)
            { // Y loop
                float Y = v.y(j);
                
                // If we can't brighten the image, skip this point.
                if (v.mode == SOLVE_BOOL && scale <= v.intensity[v.nj - j - 1][i])
                    continue;

                // Evaluate tree                        
                tree->eval(X, Y, Z);
                
                // Fill in greyscale image
                if (v.mode == SOLVE_BOOL) {
                    if (tree->root->result_bool)
                        v.intensity[v.nj - j - 1][i] = scale;
                }
                
                // Fill in color image
                else if (v.mode == SOLVE_RGB) {
                    int result = tree->root->result_color;
                    
                    // Extract colors from bit-field
                    unsigned char r = (result & 255) * scale,
                                  g = ((result >> 8) & 255) * scale,
                                  b = ((result >> 16) & 255) * scale;
                                  
                    // Only brighten the image.
                    if (r > v.red[v.nj - j - 1][i])
                        v.red[v.nj - j - 1][i] = r;
                    if (g > v.green[v.nj - j - 1][i])
                        v.green[v.nj - j - 1][i] = g;
                    if (b > v.blue[v.nj - j - 1][i])
                        v.blue[v.nj - j - 1][i] = b;
                }
                
            } // Y loop
        } // X loop
    } // Z loop
}

///////////////////////////////////////////////////////////////////////////////

void Solver::make_new_thread(MathTree* T, Region R, ThreadList& thread_list)
{
    thread* newThread = new thread;
    MathTree* newTree = T->clone();
    
    *newThread = thread(&Solver::evaluate_region, this, newTree, R);
    thread_list.push_back(make_pair(newThread, newTree));
}

///////////////////////////////////////////////////////////////////////////////

void Solver::wait_for_threads(ThreadList& thread_list)
{
    while (!thread_list.empty())
    {
        ThreadList::iterator it = thread_list.begin();
        while(it != thread_list.end())
            if (it->first->timed_join(boost::system_time()))
            {
                delete it->first;
                delete it->second;
                it = thread_list.erase(it);
            } else {
                ++it;
            }
    }
}

///////////////////////////////////////////////////////////////////////////////

// Removes any regions that cannot change the image.
void Solver::cull_regions(list<Region>& subregions)
{
    list<Region>::iterator it = subregions.begin();
    
    if (v.mode == SOLVE_BOOL) {
        while (it != subregions.end()) {
            int scale = v.scale(it->kmax - 1);
            bool cull = true;
            for (int i = it->imin; i < it->imax && cull; ++i)
                for (int j = it->jmin; j < it->jmax && cull; ++j)
                    if (v.intensity[v.nj - j - 1][i] < scale)
                        cull = false;
            if (cull) {
                update_progress(it->volume);
                it = subregions.erase(it);
            }
            else
                ++it;
        }
    } else if (v.mode == SOLVE_RGB) {
        while (it != subregions.end()) {
            int scale = v.scale(it->kmax - 1) * 255;
            bool cull = true;
            for (int i = it->imin; i < it->imax && cull; ++i)
                for (int j = it->jmin; j < it->jmax && cull; ++j)
                    if (scale > v.red[v.nj - j - 1][i] ||
                        scale > v.green[v.nj - j - 1][i] ||
                        scale > v.blue[v.nj - j - 1][i])
                        cull = false;
            if (cull) {
                update_progress(it->volume);
                it = subregions.erase(it);
            } else
                ++it;
        }
    }
}

///////////////////////////////////////////////////////////////////////////////

void Solver::update_progress(long dVol)
{  
    solved_volume_lock.lock();
    solved_volume += dVol;
    
    if (solved_volume / float(full_volume) * bar_length > next_tick - 1) {
        cout << "\r    [";        
        for(int i = 0; i < next_tick; ++i)
            cout << '|';
        for(int i = next_tick; i < bar_length; ++i)
            cout << ' ';
        cout << ']';

        cout << flush;

        next_tick += 1;
    }
    solved_volume_lock.unlock();
}