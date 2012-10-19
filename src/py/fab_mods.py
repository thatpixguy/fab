#
# fab_mods.py
#    fab module definitions
#
# Neil Gershenfeld
# CBA MIT 4/21/12
#
# (c) Massachusetts Institute of Technology 2012
# Permission granted for experimental and personal use;
# license for commercial sale available from MIT.
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
   frame.formats.Append("design (.cad)")
   formats.append(".cad")
   frame.formats.Append("model (.stl)")
   formats.append(".stl")
   frame.formats.Append("expression (.math)")
   formats.append(".math")
   frame.formats.Append("drawing (.svg)")
   formats.append(".svg")
   #
   frame.processes.Append("DXF (.dxf)")
   frame.processes.Append("Epilog lasercutter (.epi)")
   workflows["image (.png) : Epilog lasercutter (.epi)"] = "make_png_epi"
   workflows["design (.cad) : Epilog lasercutter (.epi)"] = "make_cad_epi"
   workflows["expression (.math) : Epilog lasercutter (.epi)"] = "make_math_epi"
   workflows["drawing (.svg) : Epilog lasercutter (.epi)"] = "make_svg_epi"
   frame.processes.Append("Epilog halftone (.epi)")
   workflows["image (.png) : Epilog halftone (.epi)"] = "make_png_epi_halftone"
   frame.processes.Append("G-codes (.g)")
   workflows["image (.png) : G-codes (.g)"] = "make_png_g"
   workflows["design (.cad) : G-codes (.g)"] = "make_cad_g"
   workflows["expression (.math) : G-codes (.g)"] = "make_math_g"
   workflows["model (.stl) : G-codes (.g)"] = "make_stl_g"
   workflows["drawing (.svg) : G-codes (.g)"] = "make_svg_g"
   frame.processes.Append("image (.png)")
   workflows["image (.png) : image (.png)"] = "make_png_png"
   workflows["design (.cad) : image (.png)"] = "make_cad_png"
   workflows["model (.stl) : image (.png)"] = "make_stl_png"
   frame.processes.Append("model (.stl)")
   workflows["design (.cad) : model (.stl)"] = "make_cad_stl"
   frame.processes.Append("MTM Snap")
   workflows["image (.png) : MTM Snap"] = "make_png_snap"
   workflows["design (.cad) : MTM Snap"] = "make_cad_snap"
   workflows["model (.stl) : MTM Snap"] = "make_stl_snap"
   workflows["drawing (.svg) : MTM Snap"] = "make_svg_snap"
   frame.processes.Append("Omax waterjet (.ord)")
   workflows["image (.png) : Omax waterjet (.ord)"] = "make_png_ord"
   workflows["design (.cad) : Omax waterjet (.ord)"] = "make_cad_ord"
   workflows["expression (.math) : Omax waterjet (.ord)"] = "make_math_ord"
   workflows["drawing (.svg) : Omax waterjet (.ord)"] = "make_svg_ord"
   frame.processes.Append("PostScript (.ps)")
   workflows["image (.png) : PostScript (.ps)"] = "make_png_ps"
   workflows["design (.cad) : PostScript (.ps)"] = "make_cad_ps"
   workflows["expression (.math) : PostScript (.ps)"] = "make_math_ps"
   frame.processes.Append("PostScript halftone (.ps)")
   workflows["image (.png) : PostScript halftone (.ps)"] = "make_png_ps_halftone"
   frame.processes.Append("Resonetics excimer (.oms)")
   frame.processes.Append("Roland Modela (.rml)")
   workflows["image (.png) : Roland Modela (.rml)"] = "make_png_rml"
   workflows["design (.cad) : Roland Modela (.rml)"] = "make_cad_rml"
   workflows["expression (.math) : Roland Modela (.rml)"] = "make_math_rml"
   workflows["model (.stl) : Roland Modela (.rml)"] = "make_stl_rml"
   workflows["drawing (.svg) : Roland Modela (.rml)"] = "make_svg_rml"
   workflows["image (.png) : Roland Modela (.rml)"] = "make_png_rml"
   frame.processes.Append("Roland vinylcutter (.camm)")
   workflows["image (.png) : Roland vinylcutter (.camm)"] = "make_png_camm"
   workflows["design (.cad) : Roland vinylcutter (.camm)"] = "make_cad_camm"
   workflows["expression (.math) : Roland vinylcutter (.camm)"] = "make_math_camm"
   workflows["drawing (.svg) : Roland vinylcutter (.camm)"] = "make_svg_camm"
   frame.processes.Append("ShopBot (.sbp)")
   workflows["image (.png) : ShopBot (.sbp)"] = "make_png_sbp"
   workflows["design (.cad) : ShopBot (.sbp)"] = "make_cad_sbp"
   workflows["expression (.math) : ShopBot (.sbp)"] = "make_math_sbp"
   workflows["model (.stl) : ShopBot (.sbp)"] = "make_stl_sbp"
   workflows["drawing (.svg) : ShopBot (.sbp)"] = "make_svg_sbp"
   frame.processes.Append("Univeral lasercutter (.uni)")
   workflows["image (.png) : Universal lasercutter (.uni)"] = "make_png_uni"
   workflows["design (.cad) : Universal lasercutter (.uni)"] = "make_cad_uni"
   workflows["expression (.math) : Universal lasercutter (.uni)"] = "make_math_uni"
   workflows["drawing (.svg) : Universal lasercutter (.uni)"] = "make_svg_uni"
   frame.processes.Append("Universal halftone (.uni)")
   workflows["image (.png) : Universal halftone (.epi)"] = "make_png_uni_halftone"
