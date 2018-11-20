cmake_minimum_required(VERSION 3.0)

# Force cmake to use the NEW policy regaringthe "VERSION" management.
cmake_policy(SET CMP0048 NEW)

project(ModelOrderReduction VERSION 1.0)

option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)


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
#include(src/gui/morGUI.cmake)

find_package(SofaFramework REQUIRED)

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction SofaMiscFem)


target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")

# Config files and install rules for pythons scripts
sofa_set_python_directory(${PROJECT_NAME} "python")

## Install rules for the library and headers; CMake package configurations files
sofa_create_package(ModelOrderReduction ${PROJECT_VERSION} ${PROJECT_NAME} ModelOrderReduction)

# if(SOFA_BUILD_TESTS)
#     add_subdirectory(src/component/ModelOrderReduction_test)
# endif()
