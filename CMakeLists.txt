cmake_minimum_required(VERSION 3.0)

# Force cmake to use the NEW policy regaringthe "VERSION" management.
cmake_policy(SET CMP0048 NEW)

project(ModelOrderReduction VERSION 1.0)

option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11" )

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
include(src/gui/morGUI.cmake)

find_package(SofaFramework REQUIRED)

set(TEST_CUDA OFF)

if (TEST_CUDA) # ENABLE_CUDA

    find_package(CUDA REQUIRED)
    message("CUDA SET --> WILL BE USED FOR MOR")
    set(CUDA_SOURCES
        src/component/forcefield/CudaMatMult.cu
        )

    # Make the compiler definitions available to nvcc
    add_definitions("-DSOFA_BUILD_SOFACUDA")
    # Give include directories to nvcc compiler.
    # Note: keep cuda_include_directories() before cuda_add_library().
    cuda_include_directories("${CMAKE_CURRENT_SOURCE_DIR}")
    cuda_include_directories("${CMAKE_BINARY_DIR}/include")
    cuda_add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${CUDA_SOURCES} ${README_FILES})
    set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "${SOFACUDA_COMPILE_DEFINITIONS}")

    #####    LIBRARY LINKS               ############################################
    target_link_libraries(${PROJECT_NAME}  SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction ${CUDA_LIBRARY} ${CUDA_cusparse_LIBRARY})


else()
    add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

    set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
    target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction)

endif()

target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")

# Config files and install rules for pythons scripts
sofa_set_python_directory(${PROJECT_NAME} "python")

## Install rules for the library and headers; CMake package configurations files
sofa_create_package(ModelOrderReduction ${PROJECT_VERSION} ${PROJECT_NAME} ModelOrderReduction)

# if(SOFA_BUILD_TESTS)
#     add_subdirectory(src/component/ModelOrderReduction_test)
# endif()
