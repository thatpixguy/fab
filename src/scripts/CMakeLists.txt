cmake_minimum_required(VERSION 2.6)

set(SCRIPTS cad_png cad_view path_view rml_move
            fab_send cad_math math_png_py math_stl_py
            png_tile eagle_png
   CACHE STRING "Script file list")

foreach(script ${SCRIPTS})
  if( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
    install(PROGRAMS ${script} DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  endif( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
endforeach(script)