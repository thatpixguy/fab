#ifndef NODE_H
#define NODE_H

#include <iostream>

#include <boost/thread.hpp>

#include "opcodes.hpp"
#include "fab_interval.hpp"
#include "region.hpp"

class Node
{
public:
    Node(opcode operation);
    virtual ~Node();
    
    virtual Node* clone() = 0;
    static Node* make(opcode op);
    
    // The eval functions store the answer of the evaluation in the
    // class variable result (or result_float and result_interval for
    // numeric values).
    virtual void eval(const float X,
                      const float Y,
                      const float Z) = 0;
    virtual void eval(const FabInterval& X,
                      const FabInterval& Y,
                      const FabInterval& Z) = 0;
    
    int add_ref() { return ++ref_count; }
    int sub_ref() { return --ref_count; }
    
    virtual void deactivate();
    virtual void activate();
    
    int get_weight() const { return weight;    }
    opcode op() const      { return operation; }
    bool is_ignored() const { return ref_count == 0; }
    Node* get_clone_address() const { return clone_address; }
    
    virtual bool operator==(const Node& rhs) = 0;
    virtual void print(std::ostream& o) const = 0;
    virtual void   dot(std::ostream& o) const;
    
    // Results are stored locally and then looked up by parents
    float result_float;
    FabInterval result_interval;
    boost::tribool result_bool;
    int result_color;
    
    // Nodes are marked if they need to be moved to the cache (with
    // a math_tree push operation), and become unmarked when moved out of the
    // cache.
    bool marked;
    
protected:
    const opcode operation;
    int ref_count;
    
    int weight;
    Node* clone_address;
};

std::ostream& operator<<(std::ostream& o, const Node& t);

////////////////////////////////////////////////////////////////////////////////
class UnaryNode : public Node
{
public:
    UnaryNode(opcode operation);
    virtual ~UnaryNode() {/*Nothing to do here*/};
    Node* clone();
        
    void deactivate();
    void activate();
    
    bool operator==(const Node& rhs);
    void print(std::ostream& o) const;
    void   dot(std::ostream& o) const;
    
    void set_child(Node* child);
protected:
    Node* child;
};
////////////////////////////////////////////////////////////////////////////////
class BinaryNode : public Node
{
public:
    BinaryNode(opcode operation);
    virtual ~BinaryNode() {/*Nothing to do here*/};
    Node* clone();
    
    void deactivate();
    void activate();
    
    bool operator==(const Node& rhs);
    void print(std::ostream& o) const;
    void   dot(std::ostream& o) const;
    
    void set_children(Node* left, Node* right);
    
protected:
    Node* left;
    Node* right;
};
////////////////////////////////////////////////////////////////////////////////
class NonaryNode : public Node
{
public:
    NonaryNode(opcode operation);
    virtual ~NonaryNode() {/*Nothing to do here*/};
    Node* clone();
    
    void deactivate();
    void activate();
    
    virtual bool operator==(const Node& rhs);
    virtual void print(std::ostream& o) const;
};

#endif
