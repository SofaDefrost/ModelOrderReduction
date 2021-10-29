include(${SOFA_CMAKE_DIR}/preProject.cmake)

set(SOURCE_FILES

    ModelOrderReduction_test.cpp
)
add_executable(${PROJECT_NAME} ${SOURCE_FILES} ${RC_FILES})

AddCompilerDefinitions("ModelOrderReduction_test_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}\"")
AddLinkerDependencies(ModelOrderReduction SofaTest)

include(${SOFA_CMAKE_DIR}/postProject.cmake)
