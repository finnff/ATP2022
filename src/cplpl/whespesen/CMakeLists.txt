cmake_minimum_required(VERSION 3.4)
project(whespesen)
add_subdirectory(pybind11)
pybind11_add_module(whespesensor main.cpp)


