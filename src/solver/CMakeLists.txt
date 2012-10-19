CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

find_package(Boost REQUIRED COMPONENTS thread)
include_directories(${Boost_INCLUDE_DIR})

find_package(PNG REQUIRED)
include_directories(${PNG_INCLUDE_DIR})

ADD_DEFINITIONS(-Wall)

ADD_DEFINITIONS(-O3)
#ADD_DEFINITIONS(-g)

ADD_LIBRARY(MathTree
            parser.cpp math_tree.cpp region.cpp
            numeric_nodes.cpp logic_nodes.cpp
            translator_nodes.cpp color_nodes.cpp
            fabvars.cpp node.cpp opcodes.cpp geometry.cpp)

ADD_EXECUTABLE(math_png math_png.cpp solver.cpp)
ADD_EXECUTABLE(math_dot math_dot.cpp)
ADD_EXECUTABLE(math_stl math_stl.cpp trisolver.cpp)
ADD_EXECUTABLE(math_svg math_svg.cpp edgesolver.cpp)

TARGET_LINK_LIBRARIES (math_png
   MathTree
   ${PNG_LIBRARY}
   ${Boost_THREAD_LIBRARY}
)
TARGET_LINK_LIBRARIES (math_dot
   MathTree
   ${PNG_LIBRARY}
   ${Boost_THREAD_LIBRARY}
)

TARGET_LINK_LIBRARIES (math_stl
   MathTree
   ${PNG_LIBRARY}
   ${Boost_THREAD_LIBRARY}
)

TARGET_LINK_LIBRARIES (math_svg
   MathTree
   ${PNG_LIBRARY}
   ${Boost_THREAD_LIBRARY}
)

if( ${CMAKE_PROJECT_NAME} MATCHES fabmod )
  install(TARGETS math_png DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  install(TARGETS math_dot DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  install(TARGETS math_stl DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
  install(TARGETS math_svg DESTINATION ${PROJECT_SOURCE_DIR}/../bin)
endif( ${CMAKE_PROJECT_NAME} MATCHES fabmod )

set(SOLVER_EXECUTABLES math_png math_dot math_stl math_svg
    CACHE STRING "Revised solver executables")
