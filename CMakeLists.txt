cmake_minimum_required(VERSION 2.8)
project(ModelOrderReduction)

option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)

set(MODELORDERREDUCTION_MAJOR_VERSION 1)
set(MODELORDERREDUCTION_MINOR_VERSION 0)
set(MODELORDERREDUCTION_VERSION ${MODELORDERREDUCTION_MAJOR_VERSION}.${MODELORDERREDUCTION_MINOR_VERSION})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11" )
message("${CMAKE_CXX_FLAGS_RELEASE}")
message("${CMAKE_CXX_FLAGS}")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}")


set(HEADER_FILES

    src/component/initModelOrderReduction.h

	)

set(SOURCE_FILES

    src/component/initModelOrderReduction.cpp

	)

set(README_FILES

    README.md

    )

include(src/component/forcefield/Forcefield_Files.cmake)
include(src/component/mapping/Mapping_Files.cmake)
include(src/component/loader/Loader_Files.cmake)

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")

find_package(SofaFramework REQUIRED)
set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction)

# Config files and install rules for pythons scripts
sofa_set_python_directory(${PROJECT_NAME} "python")

## Install rules for the library and headers; CMake package configurations files
sofa_create_package(ModelOrderReduction ${MODELORDERREDUCTION_VERSION} ${PROJECT_NAME} ModelOrderReduction)

# if(SOFA_BUILD_TESTS)
#     add_subdirectory(src/component/ModelOrderReduction_test)
# endif()

#[[
####   GPU CALCULATION CMAKE    ####

#####################################
#####     LINK SPARSE LIBRARY    ####
#####################################

#####     Link ViennaCL library  ####
#set(VIENNACL_LIBRARY_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/extlibs/ViennaCL-1.7.1/")
#set(VIENNACL_LIBRARY "${CMAKE_CURRENT_SOURCE_DIR}/src/extlibs/ViennaCL-1.7.1/build/libviennacl/libviennacl.so")

#include_directories(${VIENNACL_LIBRARY_DIRECTORY})
#target_link_libraries(${PROJECT_NAME} ${VIENNACL_LIBRARY})
#####################################

#####     Link OpenCL library    ####
#set(OPENCL_LIBRARY_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/extlibs/ViennaCL-1.7.1/CL")
#set(OPENCL_LIBRARY "/usr/local/cuda-9.0/lib64/libOpenCL.so")

#include_directories(${OPENCL_LIBRARY_DIRECTORY})
#target_link_libraries(${PROJECT_NAME} ${OPENCL_LIBRARY})

##find_package(OpenCL REQUIRED)
##target_link_libraries(${PROJECT_NAME} ${OPENCL_LIBRARY})
##===> cleaner but doesn't work, have to try it again

#####################################

#####     Link Eigen library     ####
##set(EIGEN_LIBRARY_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/extlibs/eigen3")
##include_directories(${PROJECT_NAME} PUBLIC ${EIGEN_LIBRARY_DIRECTORY})


#####################################
#####     SET COMPILER OPTION    ####
#####################################

#####  Compiler option viennacl  ####
#option(ENABLE_OPENCL "Use the OpenCL backend" ON)
#option(ENABLE_CUDA "Use the CUDA backend" OFF)
#####################################

## Targets using OpenCL
#if (ENABLE_OPENCL)

#    target_link_libraries(${PROJECT_NAME} ${OPENCL_LIBRARIES})
#    set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DVIENNACL_WITH_OPENCL")

#endif (ENABLE_OPENCL)

###find_package(OpenMP)
###if (OPENMP_FOUND)
###    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
###endif()
]]
