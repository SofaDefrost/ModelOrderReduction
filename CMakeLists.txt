cmake_minimum_required(VERSION 3.0)

project(ModelOrderReduction VERSION 1.0)

# Specify all required packages
find_package(SofaFramework REQUIRED)
find_package(SofaGeneral REQUIRED)
find_package(SofaBase REQUIRED)
find_package(SofaCommon REQUIRED)
find_package(SofaMisc REQUIRED)

find_package(SofaPython QUIET)
if(SofaPython_FOUND)
    message("SofaPyhon found")
    set(MOR_PYTHON 1) # See initModelOrderReduction.h.in
endif()

include(cmake/environment.cmake)

option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)

set(HEADER_FILES
    src/component/forcefield/HyperReducedHelper.h
    src/component/forcefield/HyperReducedHexahedronFEMForceField.h
    src/component/forcefield/HyperReducedHexahedronFEMForceField.inl
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.h
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.inl
    src/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.inl
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.inl
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.inl
    src/component/forcefield/HyperReducedTriangleFEMForceField.h
    src/component/forcefield/HyperReducedTriangleFEMForceField.inl
    src/component/forcefield/MechanicalMatrixMapperMOR.h
    src/component/forcefield/MechanicalMatrixMapperMOR.inl

    src/component/loader/MatrixLoader.h
    src/component/loader/MatrixLoader.inl

    src/component/mapping/ModelOrderReductionMapping.h
    src/component/mapping/ModelOrderReductionMapping.inl
    )
set(SOURCE_FILES
    src/component/initModelOrderReduction.cpp

    src/component/forcefield/HyperReducedHexahedronFEMForceField.cpp
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.cpp
    src/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.cpp
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.cpp
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.cpp
    src/component/forcefield/HyperReducedTriangleFEMForceField.cpp
    src/component/forcefield/MechanicalMatrixMapperMOR.cpp

    src/component/loader/MatrixLoader.cpp

    src/component/mapping/ModelOrderReductionMapping.cpp
    )
set(README_FILES
    README.md
    )

# Generate initModelOrderReduction.h from initModelOrderReduction.h.in
configure_file(src/component/initModelOrderReduction.h.in "${CMAKE_BINARY_DIR}/include/ModelOrderReduction/initModelOrderReduction.h")
install(FILES "${CMAKE_BINARY_DIR}/include/ModelOrderReduction/initModelOrderReduction.h" DESTINATION "include/ModelOrderReduction" COMPONENT headers)

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
target_link_libraries(${PROJECT_NAME}
    SofaCore # SofaFramework
    SofaBaseMechanics SofaBaseTopology # SofaBase
    SofaRigid # SofaCommon
    SofaConstraint SofaGeneralAnimationLoop  SofaGeneralSimpleFem SofaUserInteraction # SofaGeneral
    SofaMiscFem SofaMiscMapping # SofaMisc
    )
target_include_directories(${PROJECT_NAME} PUBLIC "$<INSTALL_INTERFACE:include>")
target_include_directories(${PROJECT_NAME} PUBLIC "$<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>")

# Config files and install rules for pythons scripts
if(SofaPython_FOUND)
    target_link_libraries(${PROJECT_NAME} SofaPython)
    sofa_set_python_directory(${PROJECT_NAME} "python" "python")
endif()

# Move all resources when install: examples, doc and python files
install(FILES "README.md" "LICENSE" DESTINATION .)
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

include(cmake/packaging.cmake)
