#ifndef TRANSLATOR_NODES
#define TRANSLATOR_NODES

#include "node.hpp"
#include "node_macro.hpp"

TRANSLATOR(BoolToNum, UnaryNode);
TRANSLATOR(NumToBool, UnaryNode);
TRANSLATOR(BoolToColor, UnaryNode);
TRANSLATOR(NumToColor, UnaryNode);

#endif