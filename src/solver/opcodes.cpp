#include <iostream>
#include <sstream>

#include "opcodes.hpp"

using namespace std;

int get_precedence(opcode op)
{
    switch (op)
    {
        case OP_NOT:
        case OP_NEGATIVE:
        case COLOR_NOT:
            return 1;
        case OP_MULT:
        case OP_DIV:
            return 2;
        case OP_PLUS:
        case OP_MINUS:
            return 3;
        case OP_LT:
        case OP_GT:
        case OP_LEQ:
        case OP_GEQ:
        case OP_NEQ:
            return 4;
        case OP_AND:
        case COLOR_AND:
            return 5;
        case OP_OR:
        case COLOR_OR:
            return 6;
        default:
            return 100;
    }
}

// get_node_type
//
//      From an opcode, infer the type of the node.
//      (e.g. cosine implies a numerical node)
node_type get_node_type(opcode op)
{
    switch (op)
    {
        case OP_ABS:
        case OP_COS:
        case OP_SIN:
        case OP_ACOS:
        case OP_ASIN:
        case OP_ATAN:
        case OP_SQRT:
        case OP_NEGATIVE:
        case OP_EXP:
        case OP_SGN:
        case OP_PLUS:
        case OP_MINUS:
        case OP_MULT:
        case OP_DIV:
        case OP_ATAN2:
        case OP_POW:
        case OP_MIN:
        case OP_MAX:
        case VAR_X:
        case VAR_Y:
        case VAR_Z:
        case NUM_CONST:
            return NODE_NUM;
        case OP_AND:
        case OP_OR:
        case OP_NOT:
        case OP_NEQ:
            return NODE_LOGIC;
        case OP_LT:
        case OP_LEQ:
        case OP_GT:
        case OP_GEQ:
            return NODE_TRANS;
        case COLOR_AND:
        case COLOR_OR:
        case COLOR_NOT:
            return NODE_COLOR;
        default:
            cerr << "Error: unknown operator " << op << " in get_node_type." << endl;
            exit(1);
        }
}

// get_token_type
//
//      From an opcode, infer the type of the token.
//      (e.g. cosine implies a function node)
Parser::token_type get_token_type(opcode op)
{
    switch (op)
    {
        case OP_ABS:
        case OP_COS:
        case OP_SIN:
        case OP_ACOS:
        case OP_ASIN:
        case OP_ATAN:
        case OP_SQRT:
        case OP_ATAN2:
        case OP_POW:
        case OP_MIN:
        case OP_MAX:
        case OP_EXP:
        case OP_SGN:
        case NUM2BOOL:
        case BOOL2NUM:
        case NUM2COLOR:
        case BOOL2COLOR:
            return Parser::TOKEN_FUNC;
        case OP_NEGATIVE:
        case OP_PLUS:
        case OP_MINUS:
        case OP_MULT:
        case OP_DIV:
        case OP_AND:
        case OP_OR:
        case OP_NOT:
        case OP_LT:
        case OP_LEQ:
        case OP_GT:
        case OP_GEQ:
        case OP_NEQ:
        case COLOR_OR:
        case COLOR_AND:
        case COLOR_NOT:
            return Parser::TOKEN_OP;
        case VAR_X:
        case VAR_Y:
        case VAR_Z:
        case NUM_CONST:
            return Parser::TOKEN_NUM;
        default:
            cerr << "Error: unknown operator " << op << " in get_token_type." << endl;
            exit(1);
        }
}

Parser::io_type get_output(opcode op)
{
    // Special case for translator nodes
    switch (op) {
        case BOOL2NUM:
            return Parser::IO_NUM;
        case NUM2BOOL:
            return Parser::IO_BOOL;
        case BOOL2COLOR:
        case NUM2COLOR:
            return Parser::IO_COLOR;
        default:
            ; // Continue to the rest of the function
    }

    node_type ntype = get_node_type(op);
    switch (ntype)
    {
        case NODE_NUM:
            return Parser::IO_NUM;
        case NODE_TRANS:
        case NODE_LOGIC:
            return Parser::IO_BOOL;
        case NODE_COLOR:
            return Parser::IO_COLOR;
        default:
            return Parser::IO_NONE;
    }
}

Parser::io_type get_input(opcode op)
{
    // Special case for translator nodes
    switch (op) {
        case BOOL2NUM:
        case BOOL2COLOR:
            return Parser::IO_BOOL;
        case NUM2BOOL:
        case NUM2COLOR:
            return Parser::IO_NUM;
        default:
            ; // Continue to the rest of the function
    }
    
    node_type ntype = get_node_type(op);
    switch (ntype)
    {
        case NODE_NUM:
        case NODE_TRANS:
            return Parser::IO_NUM;
        case NODE_LOGIC:
            return Parser::IO_BOOL;
        case NODE_COLOR:
            return Parser::IO_COLOR;
        default:
            return Parser::IO_NONE;
    }
}

// get_argcount
//
//      From an opcode, infer the number of arguments that a node will want
//      to take (e.g. cosine wants one, atan2 wants 2)
int get_argcount(opcode op)
{
    switch (op)
    {
        case NUM_CONST:
        case VAR_X:
        case VAR_Y:
        case VAR_Z:
            return 0;
        case OP_NEGATIVE:
        case OP_EXP:
        case OP_SGN:
        case OP_ABS:
        case OP_COS: 
        case OP_SIN: 
        case OP_ACOS:
        case OP_ASIN:
        case OP_ATAN: 
        case OP_SQRT:
        case OP_NOT:
        case COLOR_NOT:
            return 1;
        default:
            return 2;
        }
}

// get_associativity
//
//      From an opcode, return the associativity of the operation.
char get_associativity(opcode op)
{
    switch (op)
    {
        case OP_NEGATIVE:
        case OP_NOT:
        case COLOR_NOT:
            return 'r';
        default:
            return 'l';
    }
}

string dot_color(opcode op)
{
    if (op == VAR_X || op == VAR_Y || op == VAR_Z)
        return "red";
    else if (op == NUM_CONST)
        return "orangered";
        
    switch (get_output(op)) {
        case Parser::IO_NUM:
            return "goldenrod";
        case Parser::IO_BOOL:
            return get_input(op) == Parser::IO_NUM ? "green" : "dodgerblue";
        case Parser::IO_COLOR:
            return "palevioletred2";
        default:
            return "black";
    }
}

string dot_arrow(opcode op)
{
    switch (get_input(op)) {
        case Parser::IO_NUM:
            return "darkgoldenrod";
        case Parser::IO_BOOL:
            return "dodgerblue4";
        case Parser::IO_COLOR:
            return "palevioletred4";
        default:
            return "grey"; 
    }
}

string dot_shape(opcode op)
{
    if (op == NUM_CONST)
        return "oval";
    else if (get_token_type(op) == Parser::TOKEN_FUNC)
        return "rectangle";
    else
        return "square";
}

string dot_label(opcode op)
{
    stringstream ss;
    
    switch (op) {
        case OP_NEGATIVE:
        case OP_MINUS:
            return "−";
        case OP_MULT:
            return "×";
        default:
            ss << op;
    }
    
    return ss.str();
}   

ostream& operator<<(ostream& o, const opcode& op)
{
    switch(op)
    {
        case OP_AND:
            o << " && "; return o;
        case OP_OR:
            o << " || "; return o;
        case OP_NOT:
            o << "!"; return o;
        case OP_LT:
            o << "<"; return o;
        case OP_LEQ:
            o << "<="; return o;
        case OP_GT:
            o << ">"; return o;
        case OP_GEQ:
            o << ">="; return o;
        case OP_NEQ:
            o << "!="; return o;
        case OP_ABS:
            o << "abs"; return o;
        case OP_COS:
            o << "cos"; return o;
        case OP_SIN:
            o << "sin"; return o;
        case OP_ACOS:
            o << "acos"; return o;
        case OP_ASIN: 
            o << "asin"; return o;
        case OP_ATAN:
            o << "atan"; return o;
        case OP_SQRT:
            o << "sqrt"; return o;
        case OP_NEGATIVE:
            o << "-"; return o;
        case OP_EXP:
            o << "exp"; return o;
        case OP_SGN:
            o << "sgn"; return o;
        case OP_PLUS:
            o << "+"; return o;
        case OP_MINUS: 
            o << "-"; return o;
        case OP_MULT:
            o << "*"; return o;
        case OP_DIV: 
            o << "/"; return o;
        case OP_ATAN2:
            o << "atan2"; return o;
        case OP_POW:
            o << "pow"; return o;
        case OP_MIN:
            o << "min"; return o;
        case OP_MAX:
            o << "max"; return o;
        case NUM_CONST:
            return o;
        case VAR_X:
            o << "X"; return o;
        case VAR_Y:
            o << "Y"; return o;
        case VAR_Z:
            o << "Z"; return o;
        case COLOR_AND:
            o << "&"; return o;
        case COLOR_OR:
            o << "|"; return o;
        case COLOR_NOT:
            o << "~"; return o;
        case BOOL2NUM:
            o << "bool2num"; return o;
        case NUM2BOOL:
            o << "num2bool"; return o;
        case BOOL2COLOR:
            o << "bool2color"; return o;
        case NUM2COLOR:
            o << "num2color"; return o;
        default:
            o << "???"; return o;
    }
    return o;
}