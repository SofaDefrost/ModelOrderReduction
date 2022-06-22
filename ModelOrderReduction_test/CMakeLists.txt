cmake_minimum_required(VERSION 3.12)

project(ModelOrderReduction_test)

sofa_find_package(ModelOrderReduction REQUIRED)
sofa_find_package(Sofa.Testing REQUIRED)
sofa_find_package(Sofa.Simulation.Graph REQUIRED)

find_package(Threads REQUIRED)

set(SOURCE_FILES
    ModelOrderReduction_test.cpp
)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} ModelOrderReduction Sofa.Testing SofaSimulationGraph)
