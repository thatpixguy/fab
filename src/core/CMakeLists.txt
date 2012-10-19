cmake_minimum_required(VERSION 2.6)

set(PROGRAMS stl_info stl_png stl_path png_size png_scale png_distances
             png_offset png_path png_halftone svg_path path_join path_array
             path_ps path_png path_rml path_sbp path_g path_camm path_epi
             path_uni path_oms path_ord
    CACHE STRING "Core program list")

find_package(PNG REQUIRED)
include_directories(${PNG_INCLUDE_DIR})

#set(CMAKE_C_FLAGS -g)
set(CMAKE_C_FLAGS -O3)

# gcc on Mac OS X requires nested functions
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fnested-functions")
endif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")

add_library(fab STATIC fab.c)

foreach(program ${PROGRAMS})
  add_executable(${program} ${program}.c)
  target_link_libraries(${program} fab ${PNG_LIBRARY})
  if( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
    install(TARGETS ${program} DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  endif( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
endforeach(program)
