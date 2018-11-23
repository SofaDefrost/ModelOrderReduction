cmake_minimum_required(VERSION 3.0)

project(ModelOrderReduction VERSION 1.0)

# Specify all required packages
find_package(SofaFramework REQUIRED)
find_package(SofaGeneral REQUIRED)
find_package(SofaBase REQUIRED)

find_package(SofaPython QUIET)
if(SofaPython_FOUND)
    message("SofaPyhon found")
    set(MOR_PYTHON 1) # See initModelOrderReduction.h.in
endif()

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

# Generate initModelOrderReduction.h from initModelOrderReduction.h.in
configure_file(src/component/initModelOrderReduction.h.in "${CMAKE_BINARY_DIR}/include/ModelOrderReduction/initModelOrderReduction.h")
install(FILES "${CMAKE_BINARY_DIR}/include/ModelOrderReduction/initModelOrderReduction.h" DESTINATION "include/initModelOrderReduction" COMPONENT headers)


# Add all cmake projects within the ModelOrderReduction plugin
include(src/component/forcefield/Forcefield_Files.cmake)
include(src/component/mapping/Mapping_Files.cmake)
include(src/component/loader/Loader_Files.cmake)
###include(src/gui/morGUI.cmake)

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
target_link_libraries(${PROJECT_NAME} SofaCore SofaConstraint SofaBaseMechanics SofaUserInteraction SofaMiscFem)


target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")
target_include_directories(${PROJECT_NAME} PUBLIC "$<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>")


# Config files and install rules for pythons scripts
if(SofaPython_FOUND)
    target_link_libraries(${PROJECT_NAME} SofaPython)
    sofa_set_python_directory(${PROJECT_NAME} "python")
endif()


# Specify the install prefix
set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install CACHE PATH "Install path prefix, prepended onto install directories." FORCE)


# Move all resources when install: examples, doc and python files
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/doc/")
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/doc/ModelOrderReduction.pdf DESTINATION doc/ COMPONENT resources)	
	if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/doc/examples/")
	    install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/doc/examples/ DESTINATION examples/ COMPONENT resources)
	endif()
endif()
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tools/")
    install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/tools/ DESTINATION tools/ COMPONENT resources)
endif()


# Install rules for the library and headers; CMake package configurations files
sofa_create_package(ModelOrderReduction ${PROJECT_VERSION} ${PROJECT_NAME} ModelOrderReduction)


# if(SOFA_BUILD_TESTS)
#     add_subdirectory(src/component/ModelOrderReduction_test)
# endif()


# Allows to use CPack (for the future)
include(CPack)