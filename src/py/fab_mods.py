#
# fab_mods.py
#    fab module definitions
#
# Neil Gershenfeld 7/1/14
# (c) Massachusetts Institute of Technology 2014
#
# This work may be reproduced, modified, distributed,
# performed, and displayed for any purpose, but must
# acknowledge the fab modules project. Copyright is
# retained and must be preserved. The work is provided
# as is; no warranty is provided, and users accept all 
# liability.
#
# imports
#
import wx,sys,os
#
# set workflows
#
def set_workflows(frame,formats,workflows):
   frame.formats.Append("image (.png)")
   formats.append(".png")
   frame.formats.Append("volume (.gif)")
   formats.append(".gif")
   frame.formats.Append("mesh (.stl)")
   formats.append(".stl")
   frame.formats.Append("drawing (.svg)")
   formats.append(".svg")
   frame.formats.Append("program (.cad)")
   formats.append(".cad")
   frame.formats.Append("expression (.math)")
   formats.append(".math")
   #
   frame.processes.Append("image (.png)")
   workflows["image (.png) : image (.png)"] = "make_png_png"
   workflows["program (.cad) : image (.png)"] = "make_cad_png"
   workflows["mesh (.stl) : image (.png)"] = "make_stl_png"
   #
   frame.processes.Append("Encapsulated PostScript (.eps)")
   workflows["image (.png) : Encapsulated PostScript (.eps)"] = "make_png_eps"
   workflows["program (.cad) : Encapsulated PostScript (.eps)"] = "make_cad_eps"
   workflows["expression (.math) : Encapsulated PostScript (.eps)"] = "make_math_eps"
   frame.processes.Append("PostScript halftone (.eps)")
   workflows["image (.png) : PostScript halftone (.eps)"] = "make_png_eps_halftone"
   #
   frame.processes.Append("DXF (.dxf)")
   workflows["image (.png) : DXF (.dxf)"] = "make_png_dxf"
   workflows["program (.cad) : DXF (.dxf)"] = "make_cad_dxf"
   workflows["expression (.math) : DXF (.dxf)"] = "make_math_dxf"
   #
   frame.processes.Append("Gerber (.grb)")
   workflows["image (.png) : Gerber (.grb)"] = "make_png_grb"
   workflows["program (.cad) : Gerber (.grb)"] = "make_cad_grb"
   workflows["expression (.math) : Gerber (.grb)"] = "make_math_grb"
   #
   frame.processes.Append("Excellon (.drl)")
   workflows["image (.png) : Excellon (.drl)"] = "make_png_drl"
   workflows["program (.cad) : Excellon (.drl)"] = "make_cad_drl"
   workflows["expression (.math) : Excellon (.drl)"] = "make_math_drl"
   #
   frame.processes.Append("Epilog lasercutter (.epi)")
   workflows["image (.png) : Epilog lasercutter (.epi)"] = "make_png_epi"
   workflows["program (.cad) : Epilog lasercutter (.epi)"] = "make_cad_epi"
   workflows["expression (.math) : Epilog lasercutter (.epi)"] = "make_math_epi"
   workflows["drawing (.svg) : Epilog lasercutter (.epi)"] = "make_svg_epi"
   frame.processes.Append("Epilog halftone (.epi)")
   workflows["image (.png) : Epilog halftone (.epi)"] = "make_png_epi_halftone"
   #
   frame.processes.Append("Universal lasercutter (.uni)")
   workflows["image (.png) : Universal lasercutter (.uni)"] = "make_png_uni"
   workflows["program (.cad) : Universal lasercutter (.uni)"] = "make_cad_uni"
   workflows["expression (.math) : Universal lasercutter (.uni)"] = "make_math_uni"
   workflows["drawing (.svg) : Universal lasercutter (.uni)"] = "make_svg_uni"
   #
   frame.processes.Append("Universal halftone (.uni)")
   workflows["image (.png) : Universal halftone (.uni)"] = "make_png_uni_halftone"
   #
   frame.processes.Append("Resonetics excimer (.oms)")
   workflows["image (.png) : Resonetics excimer (.oms)"] = "make_png_oms"
   workflows["drawing (.svg) : Resonetics excimer (.oms)"] = "make_svg_oms"
   #
   frame.processes.Append("Omax waterjet (.ord)")
   workflows["image (.png) : Omax waterjet (.ord)"] = "make_png_ord"
   workflows["program (.cad) : Omax waterjet (.ord)"] = "make_cad_ord"
   workflows["expression (.math) : Omax waterjet (.ord)"] = "make_math_ord"
   workflows["drawing (.svg) : Omax waterjet (.ord)"] = "make_svg_ord"
   #
   frame.processes.Append("mesh (.stl)")
   workflows["volume (.gif) : mesh (.stl)"] = "make_gif_stl"
   workflows["program (.cad) : mesh (.stl)"] = "make_cad_stl"
   workflows["expression (.math) : mesh (.stl)"] = "make_math_stl"
   #
   frame.processes.Append("Roland vinylcutter (.camm)")
   workflows["image (.png) : Roland vinylcutter (.camm)"] = "make_png_camm"
   workflows["program (.cad) : Roland vinylcutter (.camm)"] = "make_cad_camm"
   workflows["expression (.math) : Roland vinylcutter (.camm)"] = "make_math_camm"
   workflows["drawing (.svg) : Roland vinylcutter (.camm)"] = "make_svg_camm"
   #
   frame.processes.Append("Roland MDX-20 mill (.rml)")
   workflows["image (.png) : Roland MDX-20 mill (.rml)"] = "make_png_rml"
   workflows["program (.cad) : Roland MDX-20 mill (.rml)"] = "make_cad_rml"
   workflows["expression (.math) : Roland MDX-20 mill (.rml)"] = "make_math_rml"
   workflows["mesh (.stl) : Roland MDX-20 mill (.rml)"] = "make_stl_rml"
   workflows["drawing (.svg) : Roland MDX-20 mill (.rml)"] = "make_svg_rml"
   workflows["image (.png) : Roland MDX-20 mill (.rml)"] = "make_png_rml"
   #
   frame.processes.Append("Roland SRM-20 mill (.rml)")
   workflows["image (.png) : Roland SRM-20 mill (.rml)"] = "make_png_Roland_SRM_20"
   #
   frame.processes.Append("G-codes (.g)")
   workflows["image (.png) : G-codes (.g)"] = "make_png_g"
   workflows["program (.cad) : G-codes (.g)"] = "make_cad_g"
   workflows["expression (.math) : G-codes (.g)"] = "make_math_g"
   workflows["mesh (.stl) : G-codes (.g)"] = "make_stl_g"
   workflows["drawing (.svg) : G-codes (.g)"] = "make_svg_g"
   #
   frame.processes.Append("ShopBot (.sbp)")
   workflows["image (.png) : ShopBot (.sbp)"] = "make_png_sbp"
   workflows["program (.cad) : ShopBot (.sbp)"] = "make_cad_sbp"
   workflows["expression (.math) : ShopBot (.sbp)"] = "make_math_sbp"
   workflows["mesh (.stl) : ShopBot (.sbp)"] = "make_stl_sbp"
   workflows["drawing (.svg) : ShopBot (.sbp)"] = "make_svg_sbp"
   #
   frame.processes.Append("MTM Snap")
   workflows["image (.png) : MTM Snap"] = "make_png_snap"
   workflows["program (.cad) : MTM Snap"] = "make_cad_snap"
   workflows["mesh (.stl) : MTM Snap"] = "make_stl_snap"
   workflows["drawing (.svg) : MTM Snap"] = "make_svg_snap"
