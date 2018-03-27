
list(APPEND HEADER_FILES

    src/component/forcefield/HyperReducedTetrahedronFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronFEMForceField.inl
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.h
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.inl
    src/component/forcefield/HyperReducedTriangleFEMForceField.h
    src/component/forcefield/HyperReducedTriangleFEMForceField.inl
    src/component/forcefield/MappedMatrixForceFieldAndMass.h
    src/component/forcefield/MappedMatrixForceFieldAndMass.inl
    src/component/forcefield/MooneyRivlin.h
    src/component/forcefield/NeoHookean.h

    )

list(APPEND SOURCE_FILES

    src/component/forcefield/HyperReducedTetrahedronFEMForceField.cpp
    src/component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.cpp
    src/component/forcefield/HyperReducedTriangleFEMForceField.cpp
    src/component/forcefield/MappedMatrixForceFieldAndMass.cpp

    )

if(SOFA_WITH_EXPERIMENTAL_FEATURES==1)

    list(APPEND HEADER_FILES
        src/component/forcefield/MappedMatrixForceField.h
        src/component/forcefield/MappedMatrixForceField.inl
        )

    list(APPEND SOURCE_FILES
        src/component/forcefield/MappedMatrixForceField.cpp
        )

endif()
