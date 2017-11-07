cmake_minimum_required(VERSION 2.8)
project(ModelOrderReduction)

option(MODELORDERREDUCTION_WITH_DACCORD "Make use of the DaccordAPI to improve the GUI" OFF)
option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)

set(MODELORDERREDUCTION_MAJOR_VERSION 1)
set(MODELORDERREDUCTION_MINOR_VERSION 0)
set(MODELORDERREDUCTION_VERSION ${MODELORDERREDUCTION_MAJOR_VERSION}.${MODELORDERREDUCTION_MINOR_VERSION})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}")


set(HEADER_FILES

    initModelOrderReduction.h

	)

set(SOURCE_FILES

    initModelOrderReduction.cpp

	)

set(README_FILES

    ModelOrderReduction.txt

    )

# include(cmake/environment.cmake)
# include(cmake/utils.cmake)

include(component/forcefield/Forcefield_Files.cmake)
include(component/mapping/Mapping_Files.cmake)
include(component/loader/Loader_Files.cmake)

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

include(component/forcefield/Forcefield_Links.cmake)
include(component/mapping/Mapping_Links.cmake)
include(component/loader/Loader_Links.cmake)

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADER_FILES}")

target_include_directories(${PROJECT_NAME} PUBLIC "$<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>")
target_include_directories(${PROJECT_NAME} PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/..>")
target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")


find_package(SofaFramework REQUIRED)

if(MODELORDERREDUCTION_WITH_DACCORD)
    set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION -DSOFA_WITH_DACCORD")
    target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction SofaGuiCommon)
else()
    set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
    target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction)
endif()

## Install rules for the library and headers; CMake package configurations files
sofa_create_package(ModelOrderReduction ${MODELORDERREDUCTION_VERSION} ${PROJECT_NAME} ModelOrderReduction)

# if(SOFA_BUILD_TESTS)
#     add_subdirectory(ModelOrderReduction_test)
# endif()