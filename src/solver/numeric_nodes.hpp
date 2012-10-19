#ifndef NUMERIC_NODES_H
#define NUMERIC_NODES_H

#include "node.hpp"
#include "node_macro.hpp"

NODE(NumericAbs,  UnaryNode);
NODE(NumericCos,  UnaryNode);
NODE(NumericSin,  UnaryNode);
NODE(NumericACos, UnaryNode);
NODE(NumericASin, UnaryNode);
NODE(NumericATan, UnaryNode);
NODE(NumericSqrt, UnaryNode);
NODE(NumericNeg,  UnaryNode);
NODE(NumericExp,  UnaryNode);
NODE(NumericSgn,  UnaryNode);

NODE(NumericPlus,  BinaryNode);
NODE(NumericMinus, BinaryNode);
NODE(NumericMult,  BinaryNode);
NODE(NumericDiv,   BinaryNode);
NODE(NumericATan2, BinaryNode);
NODE(NumericPow,   BinaryNode);


// These two nodes have special forms with variables to keep track of
// selective child deactivation.
class NumericMin : public BinaryNode \
{
public:
    NumericMin();
    virtual ~NumericMin() {/*Nothing to do here*/};
    void eval(const float X,
              const float Y,
              const float Z);
    void eval(const FabInterval& X,
              const FabInterval& Y,
              const FabInterval& Z);
private:
    bool left_cached;
    bool right_cached;
};


class NumericMax : public BinaryNode \
{
public:
    NumericMax();
    virtual ~NumericMax() {/*Nothing to do here*/};
    void eval(const float X,
              const float Y,
              const float Z);
    void eval(const FabInterval& X,
              const FabInterval& Y,
              const FabInterval& Z);
private:
    bool left_cached;
    bool right_cached;
};



NODE(VarX, NonaryNode);
NODE(VarY, NonaryNode);
NODE(VarZ, NonaryNode);

// Numerical constants are a special case, because the constructor
// has a unique signature.
class NumericConst : public NonaryNode
{
public:
    NumericConst(float value);
    virtual ~NumericConst()  { /* Nothing to do here */ };
    virtual bool operator==(const Node& rhs);
    
    void eval(const float X,
              const float Y,
              const float Z) { /* Nothing to do here */ };
    void eval(const FabInterval& X,
              const FabInterval& Y,
              const FabInterval& Z) { /* Nothing to do here */ };
    void eval(const Region& r);
    
    void print(std::ostream& o) const;
    void   dot(std::ostream& o) const;
};

#endif
