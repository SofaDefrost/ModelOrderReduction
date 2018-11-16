
list(APPEND HEADER_FILES

    src/component/forcefield/HyperReducedForceField.h
    src/component/forcefield/HyperReducedHexahedronFEMForceField.h
    src/component/forcefield/HyperReducedHexahedronFEMForceField.inl
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.h
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.inl
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.inl
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.inl
    src/component/forcefield/HyperReducedTriangleFEMForceField.h
    src/component/forcefield/HyperReducedTriangleFEMForceField.inl
    src/component/forcefield/MechanicalMatrixMapperMOR.h
    src/component/forcefield/MechanicalMatrixMapperMOR.inl
    src/component/forcefield/MooneyRivlin.h
    src/component/forcefield/NeoHookean.h)

list(APPEND SOURCE_FILES

    src/component/forcefield/HyperReducedHexahedronFEMForceField.cpp
    src/component/forcefield/HyperReducedRestShapeSpringsForceField.cpp
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.cpp
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.cpp
    src/component/forcefield/HyperReducedTriangleFEMForceField.cpp
    src/component/forcefield/MechanicalMatrixMapperMOR.cpp)
