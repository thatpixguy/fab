// This is an implementation file for the solver.hpp

// It should not be compiled on its own (since a template needs to
// be instantiated with a particular class).

#include "solver.hpp"

#include "switches.hpp"
#include "task_buffer.hpp"


using namespace std;
using boost::logic::tribool;
using boost::thread;

void Solver::run()
{
    task_buffer->hello();
    
    Task task = task_buffer->next();
    
    while (task.region.volume != 0) {
        tree = task.tree;
        evaluate_region(task.region);
//        cout << "Solver::run() is done with region " << task.region
//             << "\n\tand is deleting tree " << tree << endl;
        delete tree;
        task = task_buffer->next();
    }

    save();
}

void Solver::set_buffer(TaskBuffer* b)
{
    task_buffer = b;
}