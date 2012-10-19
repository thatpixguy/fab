#include <iostream>

#include "fabvars.hpp"
#include "node.hpp"
#include "trisolver.hpp"

using namespace std;


void read_args(int argc, char** argv, FabVars& v)
{
    if (argc < 3) {
        cout << "command line: math_stl in.math out.stl [resolution [quality]]\n"
             << "   in.math = input math string file\n"
             << "   out.png = output PNG image\n"
             << "   resolution = voxels per mm (optional, default 10)\n"
             << "   quality = voxel interpolation level (default 8)\n";
        exit(1);
    }
    
    v.infile_name = argv[1];
    v.outfile_name = argv[2];

    v.pixels_per_mm = 10;
    if (argc > 3)
        v.pixels_per_mm = atof(argv[3]);
    if (argc > 4)
        v.quality = atoi(argv[4]);
}


int main(int argc, char** argv)
{
    FabVars v(OUTPUT_STL);
    read_args(argc, argv, v);
    v.load();

    if (v.mode != SOLVE_BOOL && v.mode != SOLVE_REAL) {
        cerr << "Error:  math_stl only works on Boolean or Real math strings." << endl;
        exit(4);
    }

    Parser p;
    MathTree* tree = p.parse(v.math_string, v.mode);
    if (!tree)
        return 1;

    cout << "Nodes in tree: " << tree->node_count() << endl
         << "Tree depth: " << tree->root->get_weight() << endl
         << "Evaluating (region size = " << v.ni << " x " << v.nj
                                         << " x " << v.nk << ")"
                                         << endl;
    TriSolver::evaluate(tree, v);
    cout << "Writing STL." << endl;
    v.write_stl();
    
    delete tree;
    return 0;
}