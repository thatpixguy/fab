cmake_minimum_required(VERSION 2.6)

set(PYs fab_mods.py fab_set.py panel_control.py panel_cad.py
        panel_cad_png.py panel_cad_stl.py
        panel_math.py panel_math_png.py 
        panel_png.py panel_png_png.py
        panel_png_path.py panel_png_path_halftone.py panel_path_rml.py
        panel_path_sbp.py panel_path_ord.py panel_path_camm.py
        panel_path_epi.py panel_path_uni.py panel_path_g.py
        panel_path_ps.py panel_stl.py panel_stl_png.py panel_svg.py
        panel_svg_path.py panel_path_snap.py cad_shapes.py cad_text.py
        math_string.py
   CACHE STRING "Python script list")

foreach(file ${PYs})
  if( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
    install(FILES ${file} DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  endif( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
endforeach(file)
