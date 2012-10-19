#ifndef PARSE_H
#define PARSE_H

#include <string>
#include <list>

#include "opcodes.hpp"
#include "math_tree.hpp"
#include "fabvars.hpp"

class Parser
{
public:
    Parser();
    
    /* Useful enums and structures used in parse tokens */
    
    enum token_type {
        TOKEN_NUM,
        TOKEN_FUNC,
        TOKEN_OP,
        TOKEN_LPARENS,
        TOKEN_ARGSEP,
        TOKEN_RPARENS,
        TOKEN_EMPTY,
        TOKEN_ERROR
    };
    
    enum io_type {
        IO_NUM,
        IO_BOOL,
        IO_COLOR,
        IO_NONE
    };
    
    typedef struct parse_token
    {
        parse_token();
        parse_token(token_type type);
        parse_token(Node* n);
    
        Node* n;
        int num_args;
        int precedence;
        token_type ttype;
        
        io_type input;
        io_type output;
        
        char associativity;
    } parse_token;

    /* Public parse function */
    MathTree* parse(std::string input, solver_mode& mode);
    
private:
    parse_token next_token();
    std::list<parse_token> tokenize(const char* input);
    void operator_to_stack(parse_token& o1);
    void operator_to_output(parse_token& oper);

    void cache_node(Node*& node);
    void remove_ignored();
    void cache_to_tree();


    bool simplify(parse_token& oper,
                  parse_token& lh_arg,
                  parse_token& rh_arg);    
    void convert_colors(parse_token& oper,
                        parse_token& lh_arg,
                        parse_token& rh_arg);
    void wrap_argument(parse_token& arg, io_type desired);
    void wrap_real(parse_token& arg);
    
    MathTree* tree;
    
    const char* math_string;
    const char* start;
    const char* end;
    bool unary_subtraction;
    
    std::list<parse_token> output;
    std::list<parse_token> operators;
    
    std::list<Node*> node_cache[LAST_OP];
};

std::ostream& operator<<(std::ostream& o, const Parser::token_type& t);
std::ostream& operator<<(std::ostream& o, const Parser::io_type& t);

#endif