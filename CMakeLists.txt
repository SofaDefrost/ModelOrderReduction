cmake_minimum_required(VERSION 3.1)

project(ModelOrderReduction VERSION 1.0)

include(cmake/environment.cmake)

# Specify all required packages
find_package(SofaFramework REQUIRED)
find_package(SofaConstraint REQUIRED)
find_package(SofaGeneralAnimationLoop REQUIRED)
find_package(SofaGeneralSimpleFem REQUIRED)
find_package(SofaUserInteraction REQUIRED)
find_package(SofaBase REQUIRED)
find_package(SofaRigid REQUIRED)
find_package(SofaMiscFem REQUIRED)
find_package(SofaMiscMapping REQUIRED)
find_package(SofaMiscCollision REQUIRED)

option(USE_COMPRESSED_ROW_SPARSE "Use compressed row sparse format in the mappings" ON)

set(MOR_SRC "src/ModelOrderReduction")

set(HEADER_FILES
    ${MOR_SRC}/config.h.in

    ${MOR_SRC}/component/forcefield/HyperReducedHelper.h
    ${MOR_SRC}/component/forcefield/HyperReducedHexahedronFEMForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedHexahedronFEMForceField.inl
    ${MOR_SRC}/component/forcefield/HyperReducedRestShapeSpringsForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedRestShapeSpringsForceField.inl
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.inl
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronFEMForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronFEMForceField.inl
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.inl
    ${MOR_SRC}/component/forcefield/HyperReducedTriangleFEMForceField.h
    ${MOR_SRC}/component/forcefield/HyperReducedTriangleFEMForceField.inl
    ${MOR_SRC}/component/forcefield/MechanicalMatrixMapperMOR.h
    ${MOR_SRC}/component/forcefield/MechanicalMatrixMapperMOR.inl

    ${MOR_SRC}/component/loader/MatrixLoader.h
    ${MOR_SRC}/component/loader/MatrixLoader.inl

    ${MOR_SRC}/component/mapping/ModelOrderReductionMapping.h
    ${MOR_SRC}/component/mapping/ModelOrderReductionMapping.inl
    ${MOR_SRC}/component/mapping/MORContactMapping.h
    ${MOR_SRC}/component/mapping/MORContactMapping.inl

    ${MOR_SRC}/component/contact/MORFrictionContact.h
    ${MOR_SRC}/component/contact/MORFrictionContact.inl
    ${MOR_SRC}/component/contact/MORUnilateralInteractionConstraint.h
    ${MOR_SRC}/component/contact/MORUnilateralInteractionConstraint.inl
    ${MOR_SRC}/component/contact/MORpointModel.h
    ${MOR_SRC}/component/contact/MORpointModel.inl
    )
set(SOURCE_FILES
    ${MOR_SRC}/initModelOrderReduction.cpp

    ${MOR_SRC}/component/forcefield/HyperReducedHexahedronFEMForceField.cpp
    ${MOR_SRC}/component/forcefield/HyperReducedRestShapeSpringsForceField.cpp
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.cpp
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronFEMForceField.cpp
    ${MOR_SRC}/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.cpp
    ${MOR_SRC}/component/forcefield/HyperReducedTriangleFEMForceField.cpp
    ${MOR_SRC}/component/forcefield/MechanicalMatrixMapperMOR.cpp

    ${MOR_SRC}/component/loader/MatrixLoader.cpp

    ${MOR_SRC}/component/mapping/ModelOrderReductionMapping.cpp
    ${MOR_SRC}/component/mapping/MORContactMapping.cpp

    ${MOR_SRC}/component/contact/MORFrictionContact.cpp
    ${MOR_SRC}/component/contact/MORUnilateralInteractionConstraint.cpp
    ${MOR_SRC}/component/contact/MORpointModel.cpp
    )
set(README_FILES
    README.md
    )

add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "-DSOFA_BUILD_MODELORDERREDUCTION")
target_link_libraries(${PROJECT_NAME}
    SofaCore # SofaFramework
    SofaBaseMechanics SofaBaseTopology # SofaBase
    SofaRigid # SofaCommon
    SofaConstraint SofaGeneralAnimationLoop  SofaGeneralSimpleFem SofaUserInteraction # SofaGeneral
    SofaMiscFem SofaMiscMapping SofaMiscCollision # SofaMisc
    Sofa.GL
    )

# Config files and install rules for pythons scripts
sofa_install_pythonscripts(PLUGIN_NAME ${PROJECT_NAME} PYTHONSCRIPTS_SOURCE_DIR "python")

# Move all resources when install: examples, doc and python files
install(FILES "README.md" "LICENSE" DESTINATION .)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/doc")
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/doc/ModelOrderReduction.pdf DESTINATION doc COMPONENT resources)	
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/doc/examples")
        install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/doc/examples DESTINATION . COMPONENT resources)
    endif()
endif()
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tools")
    install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/tools DESTINATION . COMPONENT resources)
endif()

## Install rules for the library and headers; CMake package configurations files
sofa_create_package_with_targets(
    PACKAGE_NAME ModelOrderReduction
    PACKAGE_VERSION ${PROJECT_VERSION}
    TARGETS ${PROJECT_NAME} AUTO_SET_TARGET_PROPERTIES
    INCLUDE_SOURCE_DIR "src"
    INCLUDE_INSTALL_DIR "ModelOrderReduction"
    RELOCATABLE "plugins"
    )

# if(SOFA_BUILD_TESTS)
#     add_subdirectory(${MOR_SRC}/component/ModelOrderReduction_test)
# endif()

include(cmake/packaging.cmake)
