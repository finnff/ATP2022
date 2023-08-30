cmake_minimum_required(VERSION 3.4)
project(aaaa)

add_subdirectory(pybind11)

add_library(wsp_mod MODULE aaaa.cpp bindings.cpp)
target_link_libraries(wsp_mod PRIVATE pybind11::module)
