#include <iostream>

#include "fabvars.hpp"
#include "node.hpp"
#include "edgesolver.hpp"

using namespace std;


void read_args(int argc, char** argv, FabVars& v)
{
    if (argc < 3) {
        cout << "command line: math_svg in.math out.svg [resolution [slices [error [quality]]]]\n"
             << "   in.math = input math string file\n"
             << "   out.png = output PNG image\n"
             << "   resolution = voxels per mm (default: 10)\n"
             << "   slices = z slices (defaults: 1 for 2D models, 10 for 3D models)\n"
             << "   error = maximum decimation error (in mm^2)\n"
             << "   quality = voxel interpolation level (default: 8)\n"
             << " Note: output svgs are in mm units.";
        exit(1);
    }
    
    v.infile_name = argv[1];
    v.outfile_name = argv[2];
    
    v.pixels_per_mm = 10;
    if (argc > 3)
        v.pixels_per_mm = atof(argv[3]);
    if (argc > 4)
        v.nk = atoi(argv[4]);
    if (argc > 5)
        v.decimation_error = atof(argv[5]);
    if (argc > 6)
        v.quality = atoi(argv[6]);
}


int main(int argc, char** argv)
{
    FabVars v(OUTPUT_SVG);
    read_args(argc, argv, v);
    v.load();
    if (v.nk > 1 and argc <= 4) // 3D object with no slices given
        v.nk = 10;

    if (v.mode != SOLVE_BOOL && v.mode != SOLVE_REAL) {
        cerr << "Error:  math_svg only works on Boolean or Real math strings." << endl;
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
    EdgeSolver::evaluate(tree, v);
    cout << "Writing SVG." << endl;
    v.write_svg();
    
    delete tree;
    return 0;
}