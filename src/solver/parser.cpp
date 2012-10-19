#include <algorithm>
#include <cstdlib>
#include <list>

#include "logic_nodes.hpp"
#include "numeric_nodes.hpp"
#include "translator_nodes.hpp"
#include "color_nodes.hpp"

#include "parser.hpp"
#include "opcodes.hpp"
#include "switches.hpp"

using namespace std;

Parser::parse_token::parse_token()
        : n(NULL), num_args(0), precedence(100),
          ttype(TOKEN_EMPTY), input(IO_NONE), output(IO_NONE)
    {
        // Nothing to do here.
    }
        
Parser::parse_token::parse_token(token_type type)
        : n(NULL), num_args(0), precedence(100),
          ttype(type), input(IO_NONE), output(IO_NONE)
    {
        // Nothing to do here.
    }
        
Parser::parse_token::parse_token(Node* n)
        : n(n),
          num_args(get_argcount(n->op())),
          precedence(get_precedence(n->op())),
          ttype(get_token_type(n->op())),
          input(get_input(n->op())),
          output(get_output(n->op())),
          associativity(get_associativity(n->op()))
    {
        // Nothing to do here.
    }


ostream& operator<<(ostream& o, const Parser::token_type& t)
{
    switch (t) {
        case Parser::TOKEN_NUM:
            o << "TOKEN_NUM"; return o;
        case Parser::TOKEN_FUNC:
            o << "TOKEN_FUNC"; return o;
        case Parser::TOKEN_OP:
            o << "TOKEN_OP"; return o;
        case Parser::TOKEN_LPARENS:
            o << "TOKEN_LPARENS"; return o;
        case Parser::TOKEN_ARGSEP:
            o << "TOKEN_ARGSEP"; return o;
        case Parser::TOKEN_RPARENS:
            o << "TOKEN_RPARENS"; return o;
        case Parser::TOKEN_ERROR:
            o << "TOKEN_ERROR"; return o;
        case Parser::TOKEN_EMPTY:
        default:
            o << "TOKEN_EMPTY"; return o;
    }
}

ostream& operator<<(ostream& o, const Parser::io_type& t)
{
    switch (t) {
        case Parser::IO_NUM:
            o << "IO_NUM"; return o;
        case Parser::IO_BOOL:
            o << "IO_BOOL"; return o;
        case Parser::IO_COLOR:
            o << "IO_COLOR"; return o;
        case Parser::IO_NONE:
        default:
            o << "IO_NONE"; return o;
    }
}

void Parser::wrap_argument(parse_token& arg, io_type desired)
{
    if (!arg.n || arg.output == desired)
        return;

//    cout << "Transforming " << *arg.n << " into ";
        
    // Transform numerical nodes into logical nodes.
    if (desired == IO_BOOL && arg.output == IO_NUM) {
        arg.n = new NumToBool(arg.n);
        arg.output = IO_BOOL;
        
    // Transform booleans into numbers
    } else if (desired == IO_NUM && arg.output == IO_BOOL) {
        arg.n = new BoolToNum(arg.n);
        arg.output = IO_NUM;

    // Transform numbers into colors
    } else if (desired == IO_COLOR && arg.output == IO_NUM) {
        arg.n = new NumToColor(arg.n);
        arg.output = IO_COLOR;    

    // Transform booleans into colors
    } else if (desired == IO_COLOR && arg.output == IO_BOOL) {
        arg.n = new BoolToColor(arg.n);
        arg.output = IO_COLOR;
    
    // If we can't wrap the operator, then return false.
    } else {
        cerr << "Error: node " << *(arg.n) << " has output of type "
             << arg.output << ", which cannot be converted to "
             << desired << endl;
        exit(1);
    }
    
    cache_node(arg.n);
}

// Wraps a real-valued node f(x, y, z) into the boolean f(x, y, z) < 0
void Parser::wrap_real(parse_token& arg)
{
    wrap_argument(arg, IO_NUM);
    
    Node* zero = new NumericConst(0);
    cache_node(zero);
    
    Node* lessThan = new TransitionLt();
    static_cast<BinaryNode*>(lessThan)->set_children(arg.n, zero);
    cache_node(lessThan);
    
    arg.n = lessThan;
    arg.output = IO_BOOL;
}

Parser::Parser()
    : math_string(NULL), start(NULL), end(NULL), unary_subtraction(true)
{
    // Nothing to do here.
}

void print_list(list<Parser::parse_token> L, ostream& o)
{
    list<Parser::parse_token>::iterator it;
    int limit = 10;
    for (it = L.begin(); it != L.end(); ++it) {
        if (it->ttype == Parser::TOKEN_LPARENS)
            o << "\t(\n";
        else if (it->ttype == Parser::TOKEN_RPARENS)
            o << "\t)\n";
        else if (it->ttype == Parser::TOKEN_ARGSEP)
            o << "\t,\n";
        else if (it->n)
            o << "\t" << *(it->n) << "\n";
        if (--limit == 0)
            return;
    }
}


void print_parse(list<Parser::parse_token> output,
                 list<Parser::parse_token> operators,
                 ostream& o)
{
    for(int i = 0; i < 80; ++i)
        o << '-';
    o << endl;
    o << "Output stack:\n";
    print_list(output, o);
    o << "Operators stack:\n";
    print_list(operators, o);
    o << endl;
}

void print_parse(list<Parser::parse_token> output,
                 list<Parser::parse_token> operators)
{
    print_parse(output, operators, cout);
}

// Stores a node in the cache, uniquifying if COMBINE_NODES is enabled.
void Parser::cache_node(Node*& node)
{
    // If this is a dummy node of some kind (e.g. parenthesis,
    // argument separator), then don't do anything.
    if (!node)
        return;
        
    opcode op = node->op();
    
#if COMBINE_NODES
    list<Node*>::iterator it;
    Node* match = NULL;

    // Look for matches
    for (it = node_cache[op].begin();
         it != node_cache[op].end();
         ++it) {
        if (**it == *(node)) {
            match = *it;
            break;
        }
    }

    // If we found a match, delete the old node and replace it with
    // the matching node.
    if (match) {
        delete node;
        node = match;
    } else {
        node_cache[op].push_front(node);
    }
#else
    node_cache[op].push_front(node);
#endif
}

// Go through the node cache and delete nodes with no references
void Parser::remove_ignored()
{
    list<Node*>::iterator it;
    bool keep_going;
    
    do {
        keep_going = false;
        
        for (int op = 0; op < LAST_OP; ++op) {
            it = node_cache[op].begin();
            while (it != node_cache[op].end()) {
                if ((**it).is_ignored()) {
                    delete *it;
                    it = node_cache[op].erase(it);
                    keep_going = true;
                } else {
                    ++it;
                }
            }
        }

    } while (keep_going);
}
    

void Parser::cache_to_tree()
{
    list<Node*>::iterator it;
    for (int op = 0; op < LAST_OP; ++op)
        for (it = node_cache[op].begin(); it != node_cache[op].end(); ++it)
            tree->add(*it);
}

void Parser::convert_colors(parse_token& oper,
                            parse_token& lh_arg,
                            parse_token& rh_arg)
{
    // If we find a boolean multiplied by a numerical value, then
    // we treat it as a color creation.
    if (oper.n->op() == OP_MULT &&
         ((rh_arg.output == IO_NUM && lh_arg.output == IO_BOOL) ||
          (lh_arg.output == IO_NUM && rh_arg.output == IO_BOOL)) )
    {
        delete oper.n;
        oper.n = new ColorAnd();
        oper.input = IO_COLOR;
        oper.output = IO_COLOR;
    }
    // Logical OR on colors -> bitwise or
    if (oper.n->op() == OP_OR && (rh_arg.output == IO_COLOR ||
                                          lh_arg.output == IO_COLOR))
    {
        delete oper.n;
        oper.n = new ColorOr();
        oper.input = IO_COLOR;
        oper.output = IO_COLOR;
    }
    // Logical AND on colors -> bitwise and
    if (oper.n->op() == OP_AND && (rh_arg.output == IO_COLOR ||
                                          lh_arg.output == IO_COLOR))
    {
        delete oper.n;
        oper.n =  new ColorAnd();
        oper.input = IO_COLOR;
        oper.output = IO_COLOR;
    }
    // Logical not on colors -> bitwise not
    if (oper.n->op() == OP_NOT && rh_arg.output == IO_COLOR)
    {
        delete oper.n;
        oper.n =  new ColorNot();
        oper.input = IO_COLOR;
        oper.output = IO_COLOR;
    }
}

bool Parser::simplify(parse_token& oper,
                      parse_token& lh_arg,
                      parse_token& rh_arg)
{
    // We're only going to simplify numeric nodes to keep life easy.
    if (oper.input != IO_NUM)
        return false;
    
    opcode op = oper.n->op();
    
    if (op == OP_PLUS) {
        // 0 + X => X
        if (lh_arg.n->marked && lh_arg.n->result_float == 0) {
            delete oper.n;
            oper.n = rh_arg.n;
            return true;
        }
        // X + 0 => X
        if (rh_arg.n->marked && rh_arg.n->result_float == 0) {
            delete oper.n;
            oper.n = lh_arg.n;
            return true;
        }
    } else if (op == OP_MINUS) {
        // X - 0 => X
        if (rh_arg.n->marked && rh_arg.n->result_float == 0) {
            delete oper.n;
            oper.n = lh_arg.n;
            return true;
        }
    } else if (op == OP_MULT) {
        // X * 0 => 0
        if (rh_arg.n->marked && rh_arg.n->result_float == 0) {
            delete oper.n;
            oper.n = rh_arg.n;
            return true;
        }
        // 0 * X => 0
        if (lh_arg.n->marked && lh_arg.n->result_float == 0) {
            delete oper.n;
            oper.n = lh_arg.n;
            return true;
        }
        // X * 1 => X
        if (rh_arg.n->marked && rh_arg.n->result_float == 1) {
            delete oper.n;
            oper.n = lh_arg.n;
            return true;
        }
        // 1 * X => X
        if (lh_arg.n->marked && lh_arg.n->result_float == 1) {
            delete oper.n;
            oper.n = rh_arg.n;
            return true;
        }
    }

    return false;
}

// operator_to_output
//
//      Find out how many arguments the operation wants to take from
//      the output stack
//      Take them off the stack and make them the operator's children
//      Put the new operation on the output stack.
void Parser::operator_to_output(parse_token& oper)
{
    if (oper.ttype == TOKEN_LPARENS)
        return;
    
//    cout << *(oper.n) << " wants to pull " << oper.num_args << " off the stack." << endl;
//    cout << "The stack has " << output.size() << endl;

    parse_token rh_arg;
    parse_token lh_arg;
    
    // Handle the first argument
    if (oper.num_args >= 1) {
        if (output.empty()) {
            cerr << "Parse failed:\n\t'" << *(oper.n)
                 << "' failed to acquire its first operand." << endl;
            exit(1);
        }
        rh_arg = output.front();
        output.pop_front();
//        cout << "Acquired " << *rh_arg.n << endl;
    }
    
    // Handle the second argument
    if (oper.num_args >= 2) {
        if (output.empty()) {
            cerr << "Parse failed:\n\t'" << *(oper.n)
                 << "' failed to acquire its second operand." << endl;
            exit(1);
        }
        lh_arg = output.front();
        output.pop_front();
//        cout << "Acquired " << *lh_arg.n << endl;
    }   
    
    // Set of special cases to handle colors correctly.
    convert_colors(oper, lh_arg, rh_arg);

    // If the argument outputs are of a different type then
    // the operator's inputs, wrap them in a lightweight
    // wrapper classes to do the conversion.
    wrap_argument(lh_arg, oper.input);
    wrap_argument(rh_arg, oper.input);

    // Simplify common arithmetic expressions (e.g. X + 0 => X)
    bool simplified = false;
#if SIMPLIFY_TREE
    simplified = simplify(oper, lh_arg, rh_arg);
#endif

    if (!simplified && oper.num_args == 1) {
        static_cast<UnaryNode*>(oper.n)->set_child(rh_arg.n);
    }
    else if (!simplified && oper.num_args == 2) {
        static_cast<BinaryNode*>(oper.n)->set_children(lh_arg.n,
                                                       rh_arg.n);
    }

    // If the node has been simplified, then don't cache it - it is already
    // cached by definition (since simplification replaces the node with one
    // of its arguments).
    if (!simplified)
        cache_node(oper.n);

    output.push_front(oper);
//    cout << "Produced node " << *oper.n << endl;
}

// operator_to_stack
//
//      Add an operator to the operator stack, while checking if precedence
//      requires removing other operators from the top of the stack.
void Parser::operator_to_stack(parse_token& o1)
{   
    while (!operators.empty())
    {
        parse_token o2 = operators.front();
        if ((o1.associativity == 'l' && o1.precedence >= o2.precedence) ||
            (o1.associativity == 'r' && o1.precedence > o2.precedence))
        {
            operators.pop_front();
            operator_to_output(o2);
        } else
            break;
    }
    operators.push_front(o1);
}

bool str_match(const char* s1, const char* s2)
{
    do
        if (*s1++ != *s2++)
            return false;
    while (*s1 && *s2);
    
    return true;
}

Parser::parse_token Parser::next_token()
{
    bool next_unary_subtraction = true;
    
    parse_token result;
    
    if (*start == '(') {
        start += 1;
        result = parse_token(TOKEN_LPARENS);
    }
    else if (*start == ')') {
        start += 1;
        next_unary_subtraction = false;
        result = parse_token(TOKEN_RPARENS);
    } else if (*start == 'X' || *start == 'x') {
        start += 1;
        next_unary_subtraction = false;
        result = new VarX();
    } else if (*start == 'Y' || *start == 'y') {
        start += 1;
        next_unary_subtraction = false;
        result = new VarY();
    } else if (*start == 'Z' || *start == 'z') {
        start += 1;
        next_unary_subtraction = false;
        result = new VarZ();
    }
    else if (*start == '-') {
        start += 1;
        if (unary_subtraction) {
            result = new NumericNeg();
        } else {
            result = new NumericMinus();
        }
    }
    else if (*start == ',') {
        start += 1;
        result = parse_token(TOKEN_ARGSEP);
    }
    else if (*start == '*') {
        start += 1;
        result = new NumericMult();
    }
    else if (*start == '+') {
        start += 1;
        result = new NumericPlus();
    }
    else if (*start == '/') {
        start += 1;
        result = new NumericDiv();
    }
    else if (str_match(start, "atan2")) {
        start += 5;
        result = new NumericATan2();
    }
    else if (str_match(start, "pow")) {
        start += 3;
        result = new NumericPow();
    }
    else if (str_match(start, "min")) {
        start += 3;
        result = new NumericMin();
    }
    else if (str_match(start, "max")) {
        start += 3;
        result = new NumericMax();
    }
    else if (str_match(start, "exp")) {
        start += 3;
        result = new NumericExp();
    }
    else if (str_match(start, "sgn")) {
        start += 3;
        result = new NumericSgn();
    }
    else if (str_match(start, "abs")) {
        start += 3;
        result = new NumericAbs();
    }
    else if (str_match(start, "cos")) {
        start += 3;
        result = new NumericCos();
    }
    else if (str_match(start, "sin")) {
        start += 3;
        result = new NumericSin();
    }
    else if (str_match(start, "acos")) {
        start += 4;
        result = new NumericACos();
    }
    else if (str_match(start, "asin")) {
        start += 4;
        result = new NumericASin();
    }
    else if (str_match(start, "atan")) {
        start += 4;
        result = new NumericATan();
    }
    else if (str_match(start, "sqrt")) {
        start += 4;
        result = new NumericSqrt();
    }
    else if (str_match(start, "<=")) {
        start += 2;
        result = new TransitionLeq();
    }
    else if (str_match(start, "<")) {
        start += 1;
        result = new TransitionLt();
    }
    else if (str_match(start, ">=")) {
        start += 2;
        result = new TransitionGeq();
    }
    else if (str_match(start, ">")) {
        start += 1;
        result = new TransitionGt();
    }
    else if (str_match(start, "!=")) {
        start += 2;
        result = new LogicNeq();
    }
    else if (*start == '!' || *start == '~') {
        start += 1;
        result = new LogicNot();
    }
    else if (str_match(start, "&&"))
    {
        start += 2;
        result = new LogicAnd();
    }
    else if (*start == '&')
    {
        start += 1;
        result = new LogicAnd();
    }
    else if (str_match(start, "||"))
    {
        start += 2;
        result = new LogicOr();
    }
    else if (*start == '|')
    {
        start += 1;
        result = new LogicOr();
    }
    else if (str_match(start, "pi"))
    {
        start += 2;
        result = new NumericConst(3.14159265358979323846);
    }
    else if ((*start >= '0' && *start <= '9') || *start == '.')
    {
        
        // Accumulated value
        float v = 0;
        
        // Divided value once we're after the decimal place
        double divider = 0;
        do {
            if (*start == '.')
                divider = 10;
            else if (divider) {
                v += float(*start - '0') / divider;
                divider *= 10;
            } else {
                v = v * 10 + (*start - '0');
            }
        
            start++;
        } while ((*start >= '0' && *start <= '9') || *start == '.');
        
        // Check for scientific notation.
        if (*start == 'e') {
            int e = 0;
            bool neg_exp = false;
            start++;
            if (*start == '-') {
                neg_exp = true;
                start++;
            } else if (*start == '+') {
                neg_exp = false;
                start++;
            }
            do {
                e = e * 10 + (*start++ - '0');
            } while (*start >= '0' && *start <= '9');
            // Negate the exponent if needed.
            e = e * (neg_exp ? -1 : 1);
            v = v * pow(10.0, e);
        }
        
        next_unary_subtraction = false;
        result = new NumericConst(v);
    }
    /*
    else if (str_match(start, "true") || str_match(start, "True"))
    {
        start += 4;
        result = new logic_bool(true);
    }
    else if (str_match(start, "false") || str_match(start, "False"))
    {
        start += 4;
        result = new logic_bool(false);
    }
    */
    else
    {
        if (*start != ' ') {
            cerr << "Warning:  Unknown token at '";
            if (string(start).size() > 10)
                cerr << string(start, start + 10) << "...'" << endl;
            else
                cerr << string(start) << "'" << endl;
        }
        start++;
        return parse_token();
    }
    
    unary_subtraction = next_unary_subtraction;
    return result;
}

list<Parser::parse_token> Parser::tokenize(const char* input)
{
    start = input;
    end = input;

    list<parse_token> token_list;

    if (*end != 0)
        while(*(++end)); // Find the end of the string
    
    while (start != end)
    {
        parse_token p = next_token();
        if (p.ttype == TOKEN_ERROR)
            return list<parse_token>();
        if (p.ttype != TOKEN_EMPTY)
            token_list.push_back(p);
    }
    
    return token_list;
}

MathTree* Parser::parse(string input, solver_mode& mode)
{
    tree = new MathTree();

    parse_token current;

    cout << "Parsing... ";
    cout.flush();

    // Convert into a c-style string    
    math_string = input.c_str();
    start = math_string;
    
    unary_subtraction = true;
    
    while (*start)
    {     
        current = next_token();
        
        // If there was a parse failure, then return.
        if (current.ttype == TOKEN_ERROR)
            return NULL;
            
        // If this token was empty, then continue.
        if (current.ttype == TOKEN_EMPTY)
            continue;
            
        if (current.ttype == TOKEN_NUM)
            operator_to_output(current);
            
        else if (current.ttype == TOKEN_FUNC)
            operators.push_front(current);
            
        else if (current.ttype == TOKEN_ARGSEP)
        {   
            if (operators.empty()) {
                cerr << "Parse error: Misplaced argument separator."
                     << endl;
                exit(1);
            }
            while (operators.front().ttype != TOKEN_LPARENS)
            {
                operator_to_output(operators.front());
                operators.pop_front();
                if (operators.empty()) {
                    cerr << "Parse error: Misplaced argument separator."
                         << endl;
                    exit(1);
                }
            }
        }
        
        else if (current.ttype == TOKEN_OP)
            operator_to_stack(current);
            
        else if (current.ttype == TOKEN_LPARENS)
            operators.push_front(current);
            
        else if (current.ttype == TOKEN_RPARENS)
        {
            if (operators.empty()) {
                cerr << "Parse error: mismatched parentheses." << endl;
                exit(1);
            }        
            while (operators.front().ttype != TOKEN_LPARENS)
            {
                operator_to_output(operators.front());
                operators.pop_front();
                if (operators.empty()) {
                    cerr << "Parse error: mismatched parentheses." << endl;
                    exit(1);
                }
            }
            operators.pop_front();
            
            // If there's a function on top of the stack, then it belongs
            // with the set of parentheses.
            if (!operators.empty() && operators.front().ttype == TOKEN_FUNC)
            {
                operator_to_output(operators.front());
                operators.pop_front();
            }
        }
    }
    
    // Finish the parse by popping operators off the stack.
    while (!operators.empty())
    {
        operator_to_output(operators.front());
        operators.pop_front();
    }

    if (!output.size())
    {
        cerr << "Parse failed:\n\tEmpty math tree." << endl;
        return NULL;
    } else if (output.size() > 1) {
        cerr << "Parse failed:\n\tInvalid math string." << endl;
        return NULL;
    }

    // Make sure that the root's output type is correct; otherwise
    // return NULL.
    if (mode == SOLVE_BOOL)
        wrap_argument(output.front(), IO_BOOL);
    else if (mode == SOLVE_RGB)
        wrap_argument(output.front(), IO_COLOR);
    else if (mode == SOLVE_REAL) {
        wrap_real(output.front());
        mode = SOLVE_BOOL;
    }
    
    // Add a watcher to the top node of the tree (so that it doesn't get
    // auto-deleted)
    Node* root = output.front().n;
    root->add_ref();

    // Delete any ignored nodes (that were optimized out of the tree)
    remove_ignored();
    
    // Convert the cache into the tree.
    cache_to_tree();

    cout << "Done." << endl;
    
    // Convert from C++ structures to C-style arrays.
    tree->pack();
    tree->set_root(root);
    
    return tree;
}