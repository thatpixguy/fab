#ifndef MATH_TREE_H
#define MATH_TREE_H

#include <list>
#include <vector>

#include "fab_interval.hpp"
#include "region.hpp"

// Forward declaration of node.
class Node;

class MathTree
{
public:
    MathTree();
    ~MathTree();
    MathTree* clone() const;
    
    void add(Node* n);

    void pack();
    void set_root(Node* r);
    
    int node_count() const;
    int depth() const { return num_levels; }

    void eval(const float X,
              const float Y,
              const float Z);
    void eval(const FabInterval& X,
              const FabInterval& Y,
              const FabInterval& Z);
        
    void push();
    void pop();
    
    void export_dot(std::string filename) const;
    
    friend std::ostream& operator<<(std::ostream& o, const MathTree& t);
    Node* root;
    
private:
    std::vector< std::list<Node*> > level_list;
    std::list<Node*> constants;

    Node*** levels;
    
    int* active_nodes;
    int num_levels;
    std::list<int>* dNodes;
};

typedef std::list<Node*>::iterator        MathTreeIter;
typedef std::list<Node*>::const_iterator  MathTreeConstIter;
std::ostream& operator<<(std::ostream& o, const MathTree& t);
#endif