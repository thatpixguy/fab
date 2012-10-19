#ifndef PROGRESS_H
#define PROGRESS_H

#include <boost/thread.hpp>

// This class draws a progress bar on the screen at regular intervals
class ProgressBar
{
public:
    /* ProgressBar()
     *
     *  Simple constructor.
     */
    ProgressBar();

    /* bool update(unsigned long delta)
     *
     *  Informs the progress bar that another delta units have been
     *  evaluated.  The progress bar may or may not redraw at this point.
     *  
     *  Returns true if the update was accepted, false otherwise.
     */
    bool update(unsigned long delta);


    // The number of units in the full render
    unsigned long full;
    
    // The number of units that have been solved
    unsigned long progress;
    
    // The next significant redraw point
    int next_tick;
    
    // Total length of the ASCII bar
    int bar_length;
    
    // Mutex to synchronize disparate threads
    boost::mutex lock;
    boost::mutex cout_lock;
};

#endif