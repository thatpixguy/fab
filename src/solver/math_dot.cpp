#include <iostream>

#include "fabvars.hpp"
#include "node.hpp"

using namespace std;

void read_args(int argc, char** argv, FabVars& v)
{
    if (argc < 3) {
        cout << "command line: math_dot in.math out.dot\n"
             << "   in.math = input math string file\n"
             << "   out.dot = output dot file\n";
        exit(1);
    }
    
    v.infile_name = argv[1];
    v.outfile_name = argv[2];
}

int main(int argc, char** argv)
{
    FabVars v(OUTPUT_NONE);
    read_args(argc, argv, v);
    v.load();

    Parser p;
    MathTree* tree = p.parse(v.math_string, v.mode);
    if (!tree)
        return 1;

    tree->export_dot(v.outfile_name);

    delete tree;
    return 0;
}