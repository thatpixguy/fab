#include <iostream>

#include "fabvars.hpp"
#include "node.hpp"
#include "solver.hpp"

using namespace std;


void read_args(int argc, char** argv, FabVars& v)
{
    if (argc < 3) {
        cout << "command line: math_png in.math out.png [resolution [slices]]\n"
             << "   in.math = input math string file\n"
             << "   out.png = output PNG image\n"
             << "   resolution = pixels per mm (optional, default 10)\n"
             << "   slices = number of z slices (optional, default full)\n";
        exit(1);
    }
    
    v.infile_name = argv[1];
    v.outfile_name = argv[2];

    v.pixels_per_mm = 10;
    if (argc > 3)
        v.pixels_per_mm = atof(argv[3]);

    if (argc > 4)
        v.nk = atoi(argv[4]);
}


int main(int argc, char** argv)
{
    FabVars v(OUTPUT_PNG);
    read_args(argc, argv, v);
    v.load();

    Parser p;
    MathTree* tree = p.parse(v.math_string, v.mode);
    if (!tree)
        return 1;

    cout << "Nodes in tree: " << tree->node_count() << endl
         << "Tree depth: " << tree->root->get_weight() << endl
         << "Evaluating (region size = " << v.ni << " x " << v.nj
                                         << " x " << v.nk << ")"
                                         << endl;
    Solver s(v);
    s.evaluate(tree);
    cout << endl;
    v.write_png();

    delete tree;
    return 0;
}