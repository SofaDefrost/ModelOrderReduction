
list(APPEND HEADER_FILES

    component/forcefield/HyperReducedTetrahedronFEMForceField.h
    component/forcefield/HyperReducedTetrahedronFEMForceField.inl
    component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.h
    component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.inl
    component/forcefield/HyperReducedTriangleFEMForceField.h
    component/forcefield/HyperReducedTriangleFEMForceField.inl
    component/forcefield/MappedMatrixForceFieldAndMass.h
    component/forcefield/MappedMatrixForceFieldAndMass.inl
    component/forcefield/MooneyRivlin.h
    component/forcefield/NeoHookean.h

    )

list(APPEND SOURCE_FILES

    component/forcefield/HyperReducedTetrahedronFEMForceField.cpp
    component/forcefield/HyperReducedTetrahedronHyperelasticityFEMForceField.cpp
    component/forcefield/HyperReducedTriangleFEMForceField.cpp
    component/forcefield/MappedMatrixForceFieldAndMass.cpp

    )

if(SOFA_WITH_EXPERIMENTAL_FEATURES==1)

    list(APPEND HEADER_FILES
        component/forcefield/MappedMatrixForceField.h
        component/forcefield/MappedMatrixForceField.inl
        )

    list(APPEND SOURCE_FILES
        component/forcefield/MappedMatrixForceField.cpp
        )

endif()
